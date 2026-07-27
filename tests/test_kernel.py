"""Tests for Korame kernel."""

import pytest
from app.kernel.models import Context, Task, Response, Event, EventType


def test_context_creation():
    """Test creating a context."""
    context = Context(user_id="user1", session_id="session1")
    assert context.user_id == "user1"
    assert context.session_id == "session1"
    assert context.timestamp is not None


def test_task_creation():
    """Test creating a task."""
    context = Context(user_id="user1")
    task = Task(
        id="task1",
        agent_name="rte",
        input_data={"requirement": "Add login feature"},
        context=context
    )
    assert task.id == "task1"
    assert task.agent_name == "rte"
    assert task.input_data["requirement"] == "Add login feature"


def test_response_creation():
    """Test creating a response."""
    response = Response(
        task_id="task1",
        agent_name="rte",
        status="success",
        data={"user_story": "As a user..."}
    )
    assert response.task_id == "task1"
    assert response.agent_name == "rte"
    assert response.status == "success"


def test_event_creation():
    """Test creating an event."""
    event = Event(
        event_type=EventType.TASK_COMPLETED,
        task_id="task1",
        agent_name="rte"
    )
    assert event.event_type == EventType.TASK_COMPLETED
    assert event.task_id == "task1"

