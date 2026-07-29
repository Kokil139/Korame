"""
API endpoints for the Developer/Testing agent workflow.

Given a finalized user story (either passed directly, or looked up from an
existing RTE conversation), runs the full Developer <-> Testing loop and, once
all todo items pass, opens a pull request.
"""

from typing import Any, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["development"])

# Global state (injected via dependency injection, same pattern as app/api/chat.py)
_workflow_engine = None
_conversation_memory = None


def set_engine(engine: Any) -> None:
    """Set the workflow engine."""
    global _workflow_engine
    _workflow_engine = engine


def set_memory(memory: Any) -> None:
    """Set the conversation memory (used to look up a story by conversation_id)."""
    global _conversation_memory
    _conversation_memory = memory


class DevelopRequest(BaseModel):
    """Request to start the Developer/Testing workflow for a finalized story."""
    story_title: str
    story: Optional[str] = None
    conversation_id: Optional[str] = None
    max_attempts_per_item: int = 3


@router.post("/develop")
async def develop(request: DevelopRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    """
    Start the Developer <-> Testing loop for a user story and return immediately.

    The loop (implement -> test -> retry -> ... -> pull request) runs as a
    background task; poll GET /api/v1/todos/{todo_list_id} to watch progress
    (which agent is active, per-task status, and the final report/PR).

    Args:
        request: Either `story` directly, or `conversation_id` to pull the
            RTE agent's finalized story from an existing conversation.

    Returns:
        The new todo_list_id to poll, plus its initial status.

    Raises:
        HTTPException: If neither story source is usable, or agents aren't ready.
    """
    if not _workflow_engine:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")

    story = request.story
    if not story and request.conversation_id:
        if not _conversation_memory:
            raise HTTPException(status_code=500, detail="Conversation memory not initialized")
        messages = _conversation_memory.get_conversation(request.conversation_id)
        assistant_messages = [m for m in messages if m.role == "assistant"]
        if not assistant_messages:
            raise HTTPException(status_code=404, detail="No finalized story found in that conversation")
        story = assistant_messages[-1].content

    if not story:
        raise HTTPException(status_code=400, detail="Provide either 'story' or 'conversation_id'")

    developer = _workflow_engine.registry.get_agent("developer")
    if not developer:
        raise HTTPException(status_code=500, detail="Developer agent not registered")

    todo_list = developer.start_run(request.story_title)

    background_tasks.add_task(
        _workflow_engine.execute_development_cycle,
        todo_list=todo_list,
        story=story,
        max_attempts_per_item=request.max_attempts_per_item,
        conversation_id=request.conversation_id,
        conversation_memory=_conversation_memory,
    )

    return {
        "todo_list_id": todo_list.id,
        "story_title": todo_list.story_title,
        "status": todo_list.status,
    }


@router.get("/todos/{todo_list_id}")
async def get_todo_list(todo_list_id: str) -> dict[str, Any]:
    """
    Get the current status of a todo list (for polling progress).

    Args:
        todo_list_id: ID returned by POST /develop

    Returns:
        Per-task status, attempt counts, and whether the whole list is complete
    """
    if not _workflow_engine:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")

    developer = _workflow_engine.registry.get_agent("developer")
    if not developer:
        raise HTTPException(status_code=500, detail="Developer agent not registered")

    todo_list = developer.todo_store.get(todo_list_id)
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo list not found")

    return {
        "todo_list_id": todo_list.id,
        "story_title": todo_list.story_title,
        "status": todo_list.status,
        "current_agent": todo_list.current_agent,
        "current_activity": todo_list.current_activity,
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "status": item.status.value,
                "attempts": item.attempts,
                # Exposed so a stuck/failing task can be diagnosed from the
                # API response directly, without needing backend log access.
                "code": item.code,
                "test_output": item.test_output,
            }
            for item in todo_list.items
        ],
        "all_complete": todo_list.is_complete(),
        "pull_request": todo_list.pull_request,
        "report": todo_list.report,
        "error": todo_list.error,
    }
