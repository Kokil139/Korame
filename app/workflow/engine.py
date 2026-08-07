"""
Workflow Engine for Korame.

Orchestrates the flow of tasks through agents and providers.
"""

import time
import uuid
from typing import Optional, Any
from app.kernel.models import Task, Response, Context
from app.kernel.registry import Registry
from app.router.model_router import ModelRouter
from app.knowledge.todos import TodoStatus
from app.agents.testing.sandbox import Sandbox
from app.utils import logger
from app.workflow.graph_engine import build_dev_test_graph, DevTestState


class WorkflowEngine:
    """
    Main workflow orchestration engine.

    For V1:
    1. Takes a task
    2. Routes to appropriate agent
    3. Agent calls model via router
    4. Returns result

    Later it will handle:
    - Multi-agent workflows
    - Agent chaining
    - Error recovery
    - Result caching
    """

    def __init__(self, registry: Registry, model_router: ModelRouter):
        """
        Initialize the workflow engine.

        Args:
            registry: Registry of agents and providers
            model_router: Router for selecting providers
        """
        self.registry = registry
        self.model_router = model_router

    async def execute(
        self,
        agent_name: str,
        input_data: dict[str, Any],
        context: Optional[Context] = None,
        task_id: Optional[str] = None
    ) -> Response:
        """
        Execute a workflow task.

        Args:
            agent_name: Name of the agent to invoke
            input_data: Input data for the agent
            context: Execution context
            task_id: Optional task ID (generated if not provided)

        Returns:
            Response from the agent
        """
        # Generate task ID if not provided
        if not task_id:
            task_id = str(uuid.uuid4())

        # Get or create context
        if not context:
            context = Context()

        # Create the task
        task = Task(
            id=task_id,
            agent_name=agent_name,
            input_data=input_data,
            context=context
        )

        # Get the agent
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return Response(
                task_id=task_id,
                agent_name=agent_name,
                status="error",
                data={},
                error=f"Agent '{agent_name}' not found in registry"
            )

        # Execute the agent
        start_time = time.time()
        try:
            response = await agent.execute(task)
            response.duration_ms = (time.time() - start_time) * 1000
            return response
        except Exception as e:
            return Response(
                task_id=task_id,
                agent_name=agent_name,
                status="error",
                data={},
                error=f"Workflow execution failed: {str(e)}",
                duration_ms=(time.time() - start_time) * 1000
            )

    async def execute_chain(
        self,
        agent_sequence: list[str],
        initial_input: dict[str, Any],
        context: Optional[Context] = None
    ) -> list[Response]:
        """
        Execute a chain of agents.

        Each agent's output becomes the next agent's input.

        Args:
            agent_sequence: List of agent names to execute in order
            initial_input: Initial input data
            context: Execution context

        Returns:
            List of responses from each agent
        """
        responses = []
        current_input = initial_input

        for agent_name in agent_sequence:
            response = await self.execute(
                agent_name=agent_name,
                input_data=current_input,
                context=context
            )
            responses.append(response)

            # If any agent fails, stop the chain
            if response.status == "error":
                break

            # Use this agent's output as input for the next agent
            current_input = response.data

        return responses

    async def execute_development_cycle(
        self,
        todo_list: Any,
        story: str,
        max_attempts_per_item: int = 10,
        conversation_id: Optional[str] = None,
        conversation_memory: Optional[Any] = None,
    ) -> dict[str, Any]:
        """
        Run the full Developer <-> Testing loop for a single finalized user story.
        Intended to run as a background task: `todo_list` is a shell already
        created (and registered in the shared TodoStore) via
        `DeveloperAgent.start_run()`, so the caller already has a
        `todo_list.id` to poll before this method does anything. Every step
        below updates `todo_list.status` / `current_agent` / `current_activity`
        in place so a GET /api/v1/todos/{id} poll sees live progress:

        1. Developer Agent breaks the story into an ordered todo list.
        2. For each todo item (one after another):
           - Developer Agent implements it.
           - Testing Agent writes and actually executes real tests against it.
           - If tests fail, the failure output is fed back to the Developer
             Agent to fix, up to `max_attempts_per_item` tries; if it still
             fails, the item is left FAILED and the loop moves on.
           - If tests pass, the item is marked COMPLETE.
        3. Once every item is COMPLETE, the Developer Agent opens a pull
           request with all the generated code (skipped gracefully if GitHub
           isn't configured).
        4. The Developer Agent reports the outcome back to the RTE agent by
           appending a status update - including the pull request link, if
           any - to the original RTE conversation, so the business user sees
           it the next time they open that chat.

        Args:
            todo_list: A shell TodoList from DeveloperAgent.start_run()
            story: The finalized user story text (with acceptance criteria)
            max_attempts_per_item: Max implement/test retries per todo item
            conversation_id: The RTE conversation this story came from, so the
                completion report can be posted back to it (optional)
            conversation_memory: The shared ConversationMemory to post the
                report into (optional; required together with conversation_id)

        Returns:
            Dict with the todo list ID, per-item status, whether every item
            completed, the pull request result (if attempted), and the
            human-readable report that was (or would be) posted back to RTE
        """
        developer = self.registry.get_agent("developer")
        tester = self.registry.get_agent("testing")
        if not developer or not tester:
            todo_list.status = "error"
            todo_list.error = "Developer/Testing agents not registered"
            return {"status": "error", "error": todo_list.error}

        # One shared workspace for the WHOLE story, not one per task: every
        # task's file lands here and stays here (not wiped the moment its own
        # test finishes), so a multi-file deliverable (e.g. every page of a
        # multi-page site) accumulates into one cohesive project, later
        # tasks' tests can regression-test earlier tasks' files too, and the
        # final PR reflects everything actually built - not just whichever
        # task happened to write to a shared generic filename last.
        sandbox = Sandbox(todo_list.id)
        try:
            await developer.populate_todo_list(todo_list, story)

            if todo_list.items:
                # LangGraph state-machine drives the implement → test → fix
                # cycle for each item, replacing the hand-rolled nested loops.
                dev_test_graph = build_dev_test_graph(
                    todo_list=todo_list,
                    story=story,
                    max_attempts=max_attempts_per_item,
                    sandbox=sandbox,
                    developer=developer,
                    tester=tester,
                )
                await dev_test_graph.ainvoke(
                    DevTestState(item_index=0, attempt=0, test_feedback=None, test_code=None, stop=False)
                )

            pull_request = None
            if todo_list.is_complete():
                todo_list.current_agent = "developer"
                todo_list.current_activity = "Opening pull request"
                pull_request = await developer.create_pull_request(todo_list, sandbox)
                todo_list.pull_request = pull_request

            todo_list.current_agent = "rte"
            todo_list.current_activity = "Reporting results back to the business user"
            report = self._build_development_report(todo_list, pull_request)
            todo_list.report = report

            # Report back to RTE: append the outcome to the original conversation
            # so the business user sees it the next time they open that chat.
            if conversation_id and conversation_memory:
                conversation_memory.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=report,
                    agent_name="rte",
                )

            todo_list.status = "complete" if todo_list.is_complete() else "failed"
            todo_list.current_agent = None
            todo_list.current_activity = "Done"

            return {
                "status": "success",
                "todo_list_id": todo_list.id,
                "story_title": todo_list.story_title,
                "items": [
                    {"id": i.id, "title": i.title, "status": i.status.value, "attempts": i.attempts}
                    for i in todo_list.items
                ],
                "all_complete": todo_list.is_complete(),
                "pull_request": pull_request,
                "report": report,
            }
        except Exception as e:
            # str(e) can be empty for some exceptions (e.g. a bare
            # NotImplementedError) - fall back to the exception type name so
            # the UI never shows a blank "Error:" with no information at all.
            # Also log the full traceback, since nothing else writes this
            # error to the application logs otherwise.
            error_message = str(e) or type(e).__name__
            logger.exception(f"Development workflow {todo_list.id} failed")
            todo_list.status = "error"
            todo_list.error = error_message
            todo_list.current_agent = None
            todo_list.current_activity = f"Error: {error_message}"
            return {"status": "error", "error": error_message}
        finally:
            # The shared workspace only needs to survive for the duration of
            # this one story's cycle (the PR, if any, was already built from
            # it above) - clean it up exactly once here, regardless of
            # whether the story succeeded, got stuck, or errored.
            sandbox.cleanup()

    async def execute_multi_story_cycle(
        self,
        story_run: Any,
        conversation_id: Optional[str] = None,
        conversation_memory: Optional[Any] = None,
        max_attempts_per_item: int = 5,
    ) -> None:
        """
        Run the Developer <-> Testing cycle for each story in a StoryRun, one
        after another - only starting the next story once the current one
        either completes or gets stuck (out of retries on some task). This is
        the "only for complex, multi-story requirements" automatic sequencing
        RTE's split decision feeds into; a single-story requirement never
        reaches this method at all (it uses execute_development_cycle()
        directly via POST /develop, unchanged).

        Reuses execute_development_cycle() as-is for each story - same
        implement -> test -> retry -> PR -> report-to-RTE behavior, just
        sequenced across multiple stories instead of a single manual trigger.

        Args:
            story_run: A StoryRun already registered in the shared StoryRunStore
            conversation_id: The RTE conversation these stories came from, so
                each story's completion report can be posted back to it
            conversation_memory: The shared ConversationMemory to post reports into
            max_attempts_per_item: Max implement/test retries per todo item,
                passed through to each story's execute_development_cycle() call
        """
        developer = self.registry.get_agent("developer")
        if not developer:
            story_run.status = "error"
            story_run.error = "Developer agent not registered"
            return

        try:
            story_run.status = "running"
            for i, (title, story) in enumerate(zip(story_run.story_titles, story_run.stories)):
                story_run.current_index = i
                todo_list = developer.start_run(title)
                story_run.todo_list_ids.append(todo_list.id)

                await self.execute_development_cycle(
                    todo_list=todo_list,
                    story=story,
                    max_attempts_per_item=max_attempts_per_item,
                    conversation_id=conversation_id,
                    conversation_memory=conversation_memory,
                )

                if not todo_list.is_complete():
                    # This story got stuck - either an internal error (todo_list.status
                    # == "error") or it simply ran out of retries on some task
                    # ("failed", with no exception at all) - either way, don't start
                    # the next story on top of an unresolved one. Surface whatever
                    # explanation is available at the story-run level too, not just
                    # buried inside this one story's own TodoList/report.
                    story_run.status = "error" if todo_list.status == "error" else "failed"
                    story_run.error = todo_list.error or (
                        f'Story "{title}" did not complete - see its task detail for specifics.'
                    )
                    return

            story_run.status = "complete"
        except Exception as e:
            error_message = str(e) or type(e).__name__
            logger.exception(f"Multi-story run {story_run.id} failed")
            story_run.status = "error"
            story_run.error = error_message

    @staticmethod
    def _build_development_report(todo_list: Any, pull_request: Optional[dict[str, Any]]) -> str:
        """Build the human-readable status update posted back to the RTE conversation."""
        lines = [f"**Development update: {todo_list.story_title}**", ""]
        icons = {
            TodoStatus.COMPLETE: "\u2705",
            TodoStatus.FAILED: "\u26a0\ufe0f",
            TodoStatus.PENDING: "\u26aa",
        }
        for item in todo_list.items:
            icon = icons.get(item.status, "\u26a0\ufe0f")
            if item.status == TodoStatus.PENDING:
                lines.append(f"{icon} {item.title} — not started (blocked by an earlier task)")
            else:
                lines.append(f"{icon} {item.title} — {item.status.value} ({item.attempts} attempt(s))")

        lines.append("")
        if todo_list.is_complete():
            if pull_request and pull_request.get("created"):
                lines.append(f"All tasks passed testing. Pull request opened: {pull_request['pr_url']}")
            elif pull_request:
                lines.append(
                    "All tasks passed testing, but the pull request could not be created: "
                    f"{pull_request.get('reason', 'unknown reason')}"
                )
        else:
            stuck = next((i for i in todo_list.items if i.status == TodoStatus.FAILED), None)
            if stuck:
                lines.append(
                    f'Stopped: "{stuck.title}" still failed testing after {stuck.attempts} attempt(s). '
                    "Latest test output:\n```\n" + (stuck.test_output or "")[-1500:] + "\n```"
                )
            else:
                lines.append("Not all tasks passed testing yet - see the statuses above.")

        return "\n".join(lines)

