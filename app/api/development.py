"""
API endpoints for the Developer/Testing agent workflow.

Given a finalized user story (either passed directly, or looked up from an
existing RTE conversation), runs the full Developer <-> Testing loop and, once
all todo items pass, opens a pull request.
"""

from typing import Any, Optional
import uuid
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from app.knowledge.todos import StoryRun

router = APIRouter(prefix="/api/v1", tags=["development"])

# Global state (injected via dependency injection, same pattern as app/api/chat.py)
_workflow_engine = None
_conversation_memory = None
_story_run_store = None


def set_engine(engine: Any) -> None:
    """Set the workflow engine."""
    global _workflow_engine
    _workflow_engine = engine


def set_memory(memory: Any) -> None:
    """Set the conversation memory (used to look up a story by conversation_id)."""
    global _conversation_memory
    _conversation_memory = memory


def set_story_run_store(store: Any) -> None:
    """Set the shared story-run store (for automatic multi-story development runs)."""
    global _story_run_store
    _story_run_store = store


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
                "file_type": item.file_type,
                "test_output": item.test_output,
            }
            for item in todo_list.items
        ],
        "all_complete": todo_list.is_complete(),
        "pull_request": todo_list.pull_request,
        "report": todo_list.report,
        "error": todo_list.error,
    }


class DevelopStoriesRequest(BaseModel):
    """Request to start automatic, sequential development across multiple stories."""
    stories: list[str]
    story_titles: list[str]
    conversation_id: Optional[str] = None
    max_attempts_per_item: int = 5


@router.post("/develop-stories")
async def develop_stories(request: DevelopStoriesRequest, background_tasks: BackgroundTasks) -> dict[str, Any]:
    """
    Start automatic, sequential development across multiple stories - used
    when RTE decided a requirement was complex enough to split into several
    independent stories. Returns immediately with a story_run_id to poll; the
    Developer works through the stories one at a time (each via the same
    implement -> test -> retry -> PR cycle as a single story), only starting
    the next once the current one completes.

    Args:
        request: The stories (and matching titles) to develop, in order

    Returns:
        The new story_run_id to poll, plus its initial status

    Raises:
        HTTPException: If the request is malformed or required services aren't ready
    """
    if not _workflow_engine:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")
    if not _story_run_store:
        raise HTTPException(status_code=500, detail="Story run store not initialized")
    if not request.stories:
        raise HTTPException(status_code=400, detail="Provide at least one story")
    if len(request.stories) != len(request.story_titles):
        raise HTTPException(status_code=400, detail="stories and story_titles must be the same length")

    story_run = StoryRun(
        id=str(uuid.uuid4()),
        story_titles=request.story_titles,
        stories=request.stories,
    )
    _story_run_store.create(story_run)

    background_tasks.add_task(
        _workflow_engine.execute_multi_story_cycle,
        story_run=story_run,
        conversation_id=request.conversation_id,
        conversation_memory=_conversation_memory,
        max_attempts_per_item=request.max_attempts_per_item,
    )

    return {"story_run_id": story_run.id, "status": story_run.status}


@router.get("/story-runs/{story_run_id}")
async def get_story_run(story_run_id: str) -> dict[str, Any]:
    """
    Get the current status of a multi-story run (for polling progress):
    which story is active, each story's own todo-list-level status, and the
    overall run status.

    Args:
        story_run_id: ID returned by POST /develop-stories

    Returns:
        Per-story status (title, todo_list_id, completion, PR) plus the
        overall run status and current story index
    """
    if not _story_run_store:
        raise HTTPException(status_code=500, detail="Story run store not initialized")

    story_run = _story_run_store.get(story_run_id)
    if not story_run:
        raise HTTPException(status_code=404, detail="Story run not found")

    developer = _workflow_engine.registry.get_agent("developer") if _workflow_engine else None

    stories = []
    for i, title in enumerate(story_run.story_titles):
        todo_list_id = story_run.todo_list_ids[i] if i < len(story_run.todo_list_ids) else None
        todo_list = developer.todo_store.get(todo_list_id) if developer and todo_list_id else None
        stories.append({
            "title": title,
            "todo_list_id": todo_list_id,
            "status": todo_list.status if todo_list else "pending",
            "all_complete": todo_list.is_complete() if todo_list else False,
            "pull_request": todo_list.pull_request if todo_list else None,
            "error": todo_list.error if todo_list else None,
        })

    return {
        "story_run_id": story_run.id,
        "status": story_run.status,
        "current_index": story_run.current_index,
        "stories": stories,
        "error": story_run.error,
    }
