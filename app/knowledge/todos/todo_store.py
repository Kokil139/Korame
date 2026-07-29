"""
Todo list tracking for the Developer/Testing agent workflow.

A finalized user story is broken into an ordered TodoList of small,
independently implementable TodoItems. The Developer Agent implements each
item; the Testing Agent verifies it. Both agents (and any status-polling API
endpoint) share the same TodoStore instance via the Knowledge Fabric, so
status updates made mid-loop are immediately visible to whoever looks the
list up next.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class TodoStatus(str, Enum):
    """Lifecycle states of a single todo item."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    FAILED = "failed"
    COMPLETE = "complete"


@dataclass
class TodoItem:
    """A single, independently implementable engineering task."""
    id: str
    title: str
    description: str = ""
    status: TodoStatus = TodoStatus.PENDING
    code: str = ""
    # "python" (default) or "html" - detected from the generated code so the
    # Testing Agent knows whether to `import` it or check it as a page.
    file_type: str = "python"
    test_code: str = ""
    test_output: str = ""
    attempts: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TodoList:
    """An ordered list of todo items generated from a single user story."""
    id: str
    story_id: str
    story_title: str
    items: list[TodoItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    # Live run status, polled by the frontend to show the workflow in progress.
    # One of: starting | planning | running | complete | failed | error
    status: str = "starting"
    current_agent: Optional[str] = None  # "rte" | "developer" | "testing" | None
    current_activity: str = "Preparing to analyze the story"
    pull_request: Optional[dict[str, Any]] = None
    report: str = ""
    error: Optional[str] = None

    def is_complete(self) -> bool:
        """True once every item has passed testing."""
        return bool(self.items) and all(item.status == TodoStatus.COMPLETE for item in self.items)

    def next_pending(self) -> Optional[TodoItem]:
        """The next item that still needs work, if any."""
        for item in self.items:
            if item.status != TodoStatus.COMPLETE:
                return item
        return None


class TodoStore:
    """In-memory store of todo lists, shared between the Developer and Testing agents."""

    def __init__(self):
        """Initialize an empty store."""
        self._lists: dict[str, TodoList] = {}

    def create(self, todo_list: TodoList) -> None:
        """Register a new todo list."""
        self._lists[todo_list.id] = todo_list

    def get(self, todo_list_id: str) -> Optional[TodoList]:
        """Get a todo list by ID."""
        return self._lists.get(todo_list_id)

    def list_all(self) -> list[TodoList]:
        """Get all tracked todo lists."""
        return list(self._lists.values())
