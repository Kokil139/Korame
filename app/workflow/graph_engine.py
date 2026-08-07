"""
LangGraph-powered developer/testing loop for Korame.

Models the implement → test → fix cycle as a LangGraph StateGraph, giving each
step an explicit node and conditional routing between them — replacing the
hand-rolled nested for loops that previously lived in WorkflowEngine.

Graph topology
--------------
START → implement → test ──┬── (pass)     → advance ──┬── (more items) → implement
                            ├── (retry)    → implement  └── (done)       → END
                            └── (exhausted)→ exhausted                   → END

State is a plain TypedDict; all mutations to the TodoList (status, logs, etc.)
happen as side effects inside the node functions so the HTTP polling endpoint
always sees live progress without needing LangGraph state to mirror the full
TodoList structure.
"""

from __future__ import annotations

from typing import Any, Optional
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.knowledge.todos import TodoStatus
from app.utils import logger


class DevTestState(TypedDict):
    """Mutable state threaded through the developer-testing graph."""

    item_index: int           # index into todo_list.items currently being worked
    attempt: int              # current attempt number for this item (0 = not started)
    test_feedback: Optional[str]  # pytest stdout/stderr from the last failed run
    test_code: Optional[str]      # the actual test source that produced that failure
    stop: bool                # set True by exhausted_node to signal the loop is blocked


def build_dev_test_graph(
    todo_list: Any,
    story: str,
    max_attempts: int,
    sandbox: Any,
    developer: Any,
    tester: Any,
):
    """
    Build and compile a LangGraph StateGraph for one story's implement/test loop.

    All agent/sandbox references are captured as closures so the compiled graph
    can be invoked with only the lightweight DevTestState dict.

    Args:
        todo_list:    The TodoList whose items to process (mutated in place).
        story:        Full user-story text forwarded to the developer each step.
        max_attempts: Max implement/test cycles per item before giving up.
        sandbox:      Sandbox instance shared across all tasks in this story.
        developer:    DeveloperAgent instance.
        tester:       TestingAgent instance.

    Returns:
        A compiled async LangGraph (call ``await graph.ainvoke(initial_state)``).
    """

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    async def implement_node(state: DevTestState) -> dict:
        """Ask the developer agent to implement (or fix) the current item."""
        new_attempt = state["attempt"] + 1
        idx = state["item_index"]
        item = todo_list.items[idx]

        if new_attempt == 1:
            item.status = TodoStatus.IN_PROGRESS

        item.attempts = new_attempt
        todo_list.current_agent = "developer"
        todo_list.current_activity = (
            f"Implementing: {item.title}"
            if new_attempt == 1
            else f"Fixing: {item.title} (attempt {new_attempt})"
        )

        item.code = await developer.implement_item(
            story, item, state["test_feedback"], state["test_code"]
        )
        item.file_type = developer.detect_file_type(item.code)
        if not item.filename:
            item.filename = developer.derive_filename(item.title, item.file_type)
        item.status = TodoStatus.TESTING

        return {"attempt": new_attempt}

    async def test_node(state: DevTestState) -> dict:
        """Ask the testing agent to verify the current item; update test_feedback."""
        idx = state["item_index"]
        item = todo_list.items[idx]
        attempt = state["attempt"]

        todo_list.current_agent = "testing"
        todo_list.current_activity = f"Testing: {item.title}"

        test_result = await tester.run_tests(
            sandbox=sandbox,
            task_title=item.title,
            code=item.code,
            file_type=item.file_type,
            filename=item.filename,
        )
        item.test_code = test_result["test_code"]
        item.test_output = test_result["output"]

        if test_result["passed"]:
            item.status = TodoStatus.COMPLETE
            logger.info(f"Task '{item.title}' passed testing on attempt {attempt}")
            return {"test_feedback": None, "test_code": None}

        item.status = TodoStatus.FAILED
        logger.warning(
            f"Task '{item.title}' failed testing (attempt {attempt}/{max_attempts}):\n"
            f"--- Generated code ---\n{item.code}\n"
            f"--- Test code ---\n{item.test_code}\n"
            f"--- Test output ---\n{test_result['output']}"
        )
        return {"test_feedback": test_result["output"], "test_code": test_result.get("test_code", "")}

    async def advance_node(state: DevTestState) -> dict:
        """Move to the next item; reset per-item state."""
        return {"item_index": state["item_index"] + 1, "attempt": 0, "test_feedback": None, "test_code": None}

    async def exhausted_node(state: DevTestState) -> dict:
        """All retries used up — mark the loop as blocked and stop."""
        idx = state["item_index"]
        item = todo_list.items[idx]
        todo_list.current_activity = (
            f"Blocked on: {item.title} "
            f"(still failing after {state['attempt']} attempt(s))"
        )
        return {"stop": True}

    # ------------------------------------------------------------------
    # Routing functions (called by add_conditional_edges)
    # ------------------------------------------------------------------

    def route_after_test(state: DevTestState) -> str:
        idx = state["item_index"]
        item = todo_list.items[idx]
        if item.status == TodoStatus.COMPLETE:
            return "advance"
        if state["attempt"] < max_attempts:
            return "retry"
        return "exhausted"

    def should_continue(state: DevTestState) -> str:
        """After advancing, decide whether there is another item to process."""
        if state["item_index"] >= len(todo_list.items):
            return END
        return "implement"

    # ------------------------------------------------------------------
    # Graph assembly
    # ------------------------------------------------------------------

    graph: StateGraph = StateGraph(DevTestState)

    graph.add_node("implement", implement_node)
    graph.add_node("test", test_node)
    graph.add_node("advance", advance_node)
    graph.add_node("exhausted", exhausted_node)

    graph.set_entry_point("implement")
    graph.add_edge("implement", "test")
    graph.add_conditional_edges(
        "test",
        route_after_test,
        {"advance": "advance", "retry": "implement", "exhausted": "exhausted"},
    )
    graph.add_conditional_edges(
        "advance",
        should_continue,
        {END: END, "implement": "implement"},
    )
    graph.add_edge("exhausted", END)

    return graph.compile()
