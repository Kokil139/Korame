"""
Model Router for intelligent provider selection.

Routes tasks to appropriate model providers based on task type, complexity, etc.
"""

from typing import Optional
from app.kernel.provider import Provider
from app.kernel.models import Task
from app.providers.ollama import OllamaProvider


class ModelRouter:
    """Routes tasks to appropriate model providers."""

    def __init__(self, default_provider: Optional[Provider] = None):
        """
        Initialize the model router.

        Args:
            default_provider: Default provider to use (e.g., Ollama)
        """
        self.default_provider = default_provider or OllamaProvider()

    def route(self, task: Task) -> Provider:
        """
        Route a task to an appropriate provider.

        For V1, this always returns the default provider (Ollama).
        Later, this will support routing based on:
        - Task type (architecture, coding, planning, etc.)
        - Task complexity
        - Available resources
        - Model capabilities

        Args:
            task: The task to route

        Returns:
            The selected provider
        """
        # V1: Always use default provider
        return self.default_provider

    def set_default_provider(self, provider: Provider) -> None:
        """Set the default provider."""
        self.default_provider = provider

    def get_default_provider(self) -> Provider:
        """Get the default provider."""
        return self.default_provider

