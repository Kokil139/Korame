"""
Model Router for intelligent provider selection.

Routes tasks to appropriate model providers based on agent name, task type, etc.
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
            default_provider: Fallback provider when no agent-specific route matches.
        """
        self.default_provider = default_provider or OllamaProvider()
        self._agent_routes: dict[str, Provider] = {}

    def register_agent_provider(self, agent_name: str, provider: Provider) -> None:
        """
        Bind a specific provider to an agent name.

        When ``route()`` is called for a task whose ``agent_name`` matches,
        this provider is returned instead of the default.

        Args:
            agent_name: Name of the agent (e.g. "rte", "developer").
            provider:   The provider to use for that agent.
        """
        self._agent_routes[agent_name] = provider

    def route(self, task: Task) -> Provider:
        """
        Route a task to the appropriate provider.

        Checks agent-specific routes first; falls back to the default provider.

        Args:
            task: The task to route.

        Returns:
            The selected provider.
        """
        return self._agent_routes.get(task.agent_name, self.default_provider)

    def set_default_provider(self, provider: Provider) -> None:
        """Set the default (fallback) provider."""
        self.default_provider = provider

    def get_default_provider(self) -> Provider:
        """Get the default (fallback) provider."""
        return self.default_provider

