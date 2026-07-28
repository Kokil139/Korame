"""
Registry for agents and providers.

Central place to register, retrieve, and manage agents and providers.
"""

from typing import Optional, Dict, Any
from app.kernel.agent import Agent
from app.kernel.provider import Provider


class Registry:
    """Registry for managing agents and providers."""

    def __init__(self):
        """Initialize the registry."""
        self._agents: Dict[str, Agent] = {}
        self._providers: Dict[str, Provider] = {}

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent.

        Args:
            agent: The agent to register

        Raises:
            ValueError: If an agent with the same name is already registered
        """
        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' is already registered")
        self._agents[agent.name] = agent

    def register_provider(self, provider: Provider) -> None:
        """
        Register a provider.

        Args:
            provider: The provider to register

        Raises:
            ValueError: If a provider with the same name is already registered
        """
        if provider.name in self._providers:
            raise ValueError(f"Provider '{provider.name}' is already registered")
        self._providers[provider.name] = provider

    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name.

        Args:
            name: The agent name

        Returns:
            The agent, or None if not found
        """
        return self._agents.get(name)

    def get_provider(self, name: str) -> Optional[Provider]:
        """
        Get a provider by name.

        Args:
            name: The provider name

        Returns:
            The provider, or None if not found
        """
        return self._providers.get(name)

    def list_agents(self) -> list[str]:
        """Get a list of all registered agent names."""
        return list(self._agents.keys())

    def list_providers(self) -> list[str]:
        """Get a list of all registered provider names."""
        return list(self._providers.keys())

    def has_agent(self, name: str) -> bool:
        """Check if an agent is registered."""
        return name in self._agents

    def has_provider(self, name: str) -> bool:
        """Check if a provider is registered."""
        return name in self._providers

