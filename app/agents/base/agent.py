"""Base agent class with common utilities."""

from typing import Any, Optional
from app.kernel.agent import Agent
from app.kernel.models import Task, Response


class BaseAgent(Agent):
    """
    Base class for all Korame agents.

    Provides common functionality like prompt loading, validation, etc.
    """

    async def execute(self, task: Task) -> Response:
        """
        Execute a task.

        This is the main entry point for agent logic.

        Args:
            task: The task to execute

        Returns:
            A Response object with the result
        """
        try:
            # Implementation will be provided by subclasses
            raise NotImplementedError(f"Agent {self.name} must implement execute()")
        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=self.name,
                status="error",
                data={},
                error=str(e)
            )

