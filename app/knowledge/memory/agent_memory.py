"""
Agent memory for Korame.

Stores agent-specific state, preferences, and context.
"""

from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentMemoryEntry:
    """A single entry in agent memory."""
    key: str
    value: Any
    agent_name: str
    agent_version: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[int] = None  # Time to live
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentMemory:
    """Stores agent-specific state and context."""

    def __init__(self):
        """Initialize agent memory."""
        self.memory: dict[str, dict[str, AgentMemoryEntry]] = {}  # agent_name -> (key -> entry)

    def store(
        self,
        agent_name: str,
        key: str,
        value: Any,
        agent_version: str = "1.0.0",
        ttl_seconds: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Store a value in agent memory.

        Args:
            agent_name: Name of the agent
            key: Memory key
            value: Value to store
            agent_version: Agent version
            ttl_seconds: Time to live in seconds (None = indefinite)
            metadata: Optional metadata
        """
        if agent_name not in self.memory:
            self.memory[agent_name] = {}

        entry = AgentMemoryEntry(
            key=key,
            value=value,
            agent_name=agent_name,
            agent_version=agent_version,
            ttl_seconds=ttl_seconds,
            metadata=metadata or {}
        )
        self.memory[agent_name][key] = entry

    def retrieve(self, agent_name: str, key: str) -> Optional[Any]:
        """
        Retrieve a value from agent memory.

        Args:
            agent_name: Name of the agent
            key: Memory key

        Returns:
            The stored value, or None if not found
        """
        if agent_name not in self.memory:
            return None

        entry = self.memory[agent_name].get(key)
        if not entry:
            return None

        # Check TTL
        if entry.ttl_seconds:
            elapsed = (datetime.utcnow() - entry.created_at).total_seconds()
            if elapsed > entry.ttl_seconds:
                # Expired
                del self.memory[agent_name][key]
                return None

        return entry.value

    def get_agent_memory(self, agent_name: str) -> dict[str, Any]:
        """
        Get all memory for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dictionary of key -> value
        """
        if agent_name not in self.memory:
            return {}

        # Filter out expired entries
        result = {}
        expired_keys = []

        for key, entry in self.memory[agent_name].items():
            if entry.ttl_seconds:
                elapsed = (datetime.utcnow() - entry.created_at).total_seconds()
                if elapsed > entry.ttl_seconds:
                    expired_keys.append(key)
                    continue

            result[key] = entry.value

        # Clean up expired entries
        for key in expired_keys:
            del self.memory[agent_name][key]

        return result

    def update(
        self,
        agent_name: str,
        key: str,
        value: Any,
        metadata: Optional[dict[str, Any]] = None
    ) -> bool:
        """
        Update a value in agent memory.

        Args:
            agent_name: Name of the agent
            key: Memory key
            value: New value
            metadata: Optional metadata to merge

        Returns:
            True if updated, False if key not found
        """
        if agent_name not in self.memory or key not in self.memory[agent_name]:
            return False

        entry = self.memory[agent_name][key]
        entry.value = value
        entry.updated_at = datetime.utcnow()

        if metadata:
            entry.metadata.update(metadata)

        return True

    def delete(self, agent_name: str, key: str) -> bool:
        """
        Delete a value from agent memory.

        Args:
            agent_name: Name of the agent
            key: Memory key

        Returns:
            True if deleted, False if key not found
        """
        if agent_name not in self.memory or key not in self.memory[agent_name]:
            return False

        del self.memory[agent_name][key]
        return True

    def clear_agent(self, agent_name: str) -> None:
        """Clear all memory for an agent."""
        if agent_name in self.memory:
            self.memory[agent_name] = {}

    def list_agents(self) -> list[str]:
        """Get list of agents with stored memory."""
        return list(self.memory.keys())

