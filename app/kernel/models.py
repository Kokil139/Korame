"""
Core data models for Korame.

These are the foundational types that all agents, providers, and workflows use.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    """Status of a response from an agent or provider."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


class EventType(str, Enum):
    """Types of events that flow through Korame."""
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    AGENT_INVOKED = "agent.invoked"
    PROVIDER_CALLED = "provider.called"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"


@dataclass
class Context:
    """
    Execution context for an agent or provider call.

    Contains ambient information like user, session, metadata, etc.
    """
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Task:
    """
    A task to be executed by an agent.

    Tasks flow through agents in the workflow.
    """
    id: str
    agent_name: str
    input_data: dict[str, Any]
    context: Context
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Response:
    """
    Response from an agent or provider.
    """
    task_id: str
    agent_name: str
    status: ResponseStatus
    data: dict[str, Any]
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Event:
    """
    An event that flows through the system.

    Used for logging, auditing, and triggering workflows.
    """
    event_type: EventType
    task_id: Optional[str] = None
    agent_name: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

