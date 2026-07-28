"""
Base provider interface.

All model providers (Ollama, OpenAI, Claude, etc.) implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from app.kernel.models import Response, Task


class Provider(ABC):
    """Abstract base class for all model providers."""

    def __init__(self, name: str):
        """
        Initialize the provider.

        Args:
            name: Name of the provider (e.g., "ollama", "openai")
        """
        self.name = name

    @abstractmethod
    async def call(self, prompt: str, **kwargs: Any) -> str:
        """
        Call the model provider.

        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            The model's response as a string

        Raises:
            Exception: If the provider call fails
        """
        pass

    async def process_task(self, task: Task) -> Response:
        """
        Process a task using this provider.

        Args:
            task: The task to process

        Returns:
            A Response object with the result
        """
        try:
            prompt = task.input_data.get("prompt", "")
            result = await self.call(prompt, **task.input_data.get("params", {}))

            return Response(
                task_id=task.id,
                agent_name=task.agent_name,
                status="success",
                data={"result": result}
            )
        except Exception as e:
            return Response(
                task_id=task.id,
                agent_name=task.agent_name,
                status="error",
                data={},
                error=str(e)
            )

