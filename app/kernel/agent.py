"""
Base agent interface.

All agents (RTE, Architect, Developer, etc.) inherit from this.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from app.kernel.models import Task, Response, Context


class Agent(ABC):
    """Abstract base class for all Korame agents."""

    def __init__(self, name: str, config: Optional[dict[str, Any]] = None):
        """
        Initialize the agent.

        Args:
            name: Name of the agent (e.g., "rte", "architect")
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}

    @abstractmethod
    async def execute(self, task: Task) -> Response:
        """
        Execute a task.

        This is the main entry point for agent logic.

        Args:
            task: The task to execute

        Returns:
            A Response object with the result
        """
        pass

    async def can_handle(self, task: Task) -> bool:
        """
        Check if this agent can handle a given task.

        Args:
            task: The task to check

        Returns:
            True if the agent can handle it, False otherwise
        """
        return task.agent_name == self.name

    def get_name(self) -> str:
        """Get the agent's name."""
        return self.name

