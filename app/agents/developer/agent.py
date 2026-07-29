"""
Developer Agent.

Takes a finalized user story from the RTE agent and breaks it into an ordered
todo list of small, implementable tasks. Implements each task, revises it when
the Testing Agent reports failures, and - once every task in the list passes -
opens a pull request with the generated code.

The step-by-step loop (implement -> test -> revise -> ... -> PR) is
orchestrated by WorkflowEngine.execute_development_cycle(), which calls the
methods on this agent directly; execute() itself only handles the "break a
story into a todo list" step, for simple one-off use via the generic
POST /api/v1/chat endpoint.
"""

import os
import ast
import re
import uuid
from typing import Any, Optional
from app.agents.base import BaseAgent
from app.kernel.models import Task, Response
from app.router.model_router import ModelRouter
from app.knowledge.todos import TodoStore, TodoList, TodoItem

_NUMBERED_ITEM_PATTERN = re.compile(r"^[ \t]*\d+[\.\)][ \t]*(.+)$", re.MULTILINE)
_CODE_BLOCK_PATTERN = re.compile(r"```(?:python|html)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
# Defensively strips a redundant "Title:"/"Task:"/"Step:" label some models
# prepend to a task line despite being told not to (see prompts/developer.md).
_LABEL_PREFIX_PATTERN = re.compile(r"^(?:title|task|step)\s*:\s*", re.IGNORECASE)
_HTML_SIGNATURE_PATTERN = re.compile(r"<!DOCTYPE\s+html|<html[\s>]", re.IGNORECASE)


class DeveloperAgent(BaseAgent):
    """Developer Agent - breaks stories into tasks, implements them, and opens PRs."""

    def __init__(
        self,
        model_router: ModelRouter,
        todo_store: TodoStore,
        github_service: Optional[Any] = None,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Args:
            model_router: Router for selecting model providers
            todo_store: Shared store of todo lists (also read by status-polling endpoints)
            github_service: Optional GitHubService used to open pull requests
            config: Optional configuration
        """
        super().__init__("developer", config or {})
        self.model_router = model_router
        self.todo_store = todo_store
        self.github_service = github_service
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        """Load the Developer agent prompt from file."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "developer.md")
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Fallback prompt if the file can't be loaded."""
        return (
            "You are an expert software developer. Break the given user story into a "
            "numbered list of small, independently implementable engineering tasks. "
            "When asked to implement one, respond with only a Python code block."
        )

    def start_run(self, story_title: str) -> TodoList:
        """
        Create an empty todo list "shell" immediately - no LLM call - so a
        caller gets a todo_list_id to start polling right away, before the
        story has even been broken into tasks yet. Call populate_todo_list()
        next to actually do that.

        Args:
            story_title: Human-readable title for the story

        Returns:
            The new TodoList (already registered in the shared TodoStore, with no items yet)
        """
        todo_list = TodoList(
            id=str(uuid.uuid4()),
            story_id=self._slugify(story_title),
            story_title=story_title,
        )
        self.todo_store.create(todo_list)
        return todo_list

    async def populate_todo_list(self, todo_list: TodoList, story: str) -> None:
        """
        Break a finalized user story into an ordered list of implementation
        tasks, populating `todo_list.items` in place (so anyone already
        polling this todo list sees the tasks appear).

        Args:
            todo_list: A shell created via start_run()
            story: The finalized user story text (with acceptance criteria)
        """
        todo_list.status = "planning"
        todo_list.current_agent = "developer"
        todo_list.current_activity = "Breaking the story into tasks"

        provider = self.model_router.default_provider
        prompt = (
            f"{self.prompt_template}\n\n"
            f"## User Story\n{story}\n\n"
            "First decide whether this story is simple enough to implement as ONE "
            "cohesive task, or whether it genuinely contains multiple independent, "
            "separable pieces of work. Most stories should be ONE task - do not "
            "invent artificial steps just to produce a longer list. Respond with a "
            "numbered list (one item if simple, more only if genuinely warranted), "
            "ordered so earlier tasks don't depend on later ones. Respond with the "
            "numbered list only."
        )
        result = await provider.call(prompt, temperature=0.4, max_tokens=1200)
        task_titles = [t.strip() for t in _NUMBERED_ITEM_PATTERN.findall(result) if t.strip()]
        task_titles = [_LABEL_PREFIX_PATTERN.sub("", t).strip() or t for t in task_titles]
        if not task_titles:
            # Model didn't follow the format; fall back to a single task for the whole story.
            task_titles = [todo_list.story_title]

        todo_list.items = [
            TodoItem(id=str(uuid.uuid4()), title=title, description=title)
            for title in task_titles
        ]
        todo_list.status = "running"

    async def implement_item(self, story: str, item: TodoItem, test_feedback: Optional[str] = None) -> str:
        """
        Generate (or revise, if test_feedback is given) code for a single todo item.

        Args:
            story: The full user story, for context
            item: The todo item being implemented
            test_feedback: Failing test output from a previous attempt, if any

        Returns:
            The generated Python source code
        """
        provider = self.model_router.default_provider
        feedback_section = ""
        if test_feedback:
            feedback_section = (
                f"\n\n## Your Previous Attempt Failed Testing\n"
                f"Test output:\n{test_feedback}\n\n"
                "Read the failure above carefully: identify the specific assertion "
                "or error, understand why it happened, and make a targeted fix. "
                "Do not rewrite the whole module from scratch unless the failure "
                "shows the entire approach was wrong."
            )

        prompt = (
            f"{self.prompt_template}\n\n"
            f"## User Story\n{story}\n\n"
            f"## Task To Implement\n{item.title}\n"
            f"{feedback_section}\n\n"
            "Write a single, COMPLETE implementation that fully implements this "
            "task - a Python module for backend/logic work, or a self-contained "
            "HTML page for a frontend/UI task (see the format rules above). Do "
            "not truncate output or leave placeholders/TODOs. Respond with ONLY "
            "the code in ONE fenced code block using the correct language tag - "
            "no explanation."
        )
        result = await provider.call(prompt, temperature=0.3, max_tokens=3000)
        return self._extract_code(result)

    async def create_pull_request(self, todo_list: TodoList) -> dict[str, Any]:
        """
        Open a pull request with the code for every completed item in the todo list.

        Args:
            todo_list: A fully-completed todo list

        Returns:
            The GitHubService result (created flag + PR URL, or a reason it wasn't created)
        """
        if not self.github_service:
            return {
                "created": False,
                "reason": "GitHub integration not configured for this agent.",
            }

        files = {
            f"generated/{todo_list.story_id}/{self._slugify(item.title)}"
            f"{'.html' if item.file_type == 'html' else '.py'}": item.code
            for item in todo_list.items
            if item.code
        }
        branch_name = f"korame/{todo_list.story_id}-{todo_list.id[:8]}"
        body_lines = [
            "Auto-generated by the Korame Developer Agent, verified by the Testing Agent.",
            "",
            f"**Story:** {todo_list.story_title}",
            "",
            "**Completed tasks:**",
        ] + [f"- [x] {item.title}" for item in todo_list.items]

        return await self.github_service.create_pull_request(
            branch_name=branch_name,
            title=f"Implement: {todo_list.story_title}",
            body="\n".join(body_lines),
            files=files,
        )

    @staticmethod
    def _extract_code(text: str) -> str:
        """Pull the code out of a fenced ```python/```html ...``` block, if present."""
        match = _CODE_BLOCK_PATTERN.search(text)
        return match.group(1).strip() if match else text.strip()

    @staticmethod
    def detect_file_type(code: str) -> str:
        """
        Detect whether generated code is a standalone HTML page or a Python
        module, so the Testing Agent can test it appropriately: an HTML page
        can't be `import`-ed like a Python module, so it needs a different
        testing strategy (structural assertions on the file's text/markup).

        Only checks the start of the content (not a full-text search) so a
        Python file that merely returns/contains an HTML string somewhere in
        its body (e.g. a Flask view) isn't mistaken for a standalone HTML page.

        Safety net: if there's no HTML signature AND the content doesn't even
        parse as valid Python, it's treated as "html" (i.e. tested via text
        assertions, not `import`) anyway - some tasks produce a markup/CSS
        fragment without a <!DOCTYPE>/<html> wrapper (e.g. a task that split
        off "styling" from "page structure"), and defaulting an unrecognized,
        non-Python fragment to "python" would guarantee a doomed import that
        can never pass no matter how many times it's retried.
        """
        head = code.lstrip()[:200]
        if _HTML_SIGNATURE_PATTERN.search(head):
            return "html"

        try:
            ast.parse(code)
        except SyntaxError:
            return "html"

        return "python"

    @staticmethod
    def _slugify(text: str) -> str:
        """Turn a title into a filesystem/branch-safe slug."""
        slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
        return slug[:50] or "task"

    async def execute(self, task: Task) -> Response:
        """
        Single-shot entry point (e.g. via POST /api/v1/chat with agent_name="developer"):
        breaks a story into a todo list. Use WorkflowEngine.execute_development_cycle()
        for the full implement -> test -> revise -> PR loop.
        """
        try:
            story = task.input_data.get("story", "")
            story_title = task.input_data.get("story_title", "Untitled story")
            if not story:
                return Response(
                    task_id=task.id,
                    agent_name=self.name,
                    status="error",
                    data={},
                    error="No story provided in task input",
                )

            todo_list = self.start_run(story_title)
            await self.populate_todo_list(todo_list, story)
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="success",
                data={
                    "todo_list_id": todo_list.id,
                    "tasks": [item.title for item in todo_list.items],
                },
            )
        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=f"Developer Agent failed: {str(e)}",
            )
