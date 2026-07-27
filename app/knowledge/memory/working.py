"""
Working memory for Korame.

Stores temporary computation state, intermediate results, and scratch space.
"""

from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MemoryScope(str, Enum):
    """Scope of a working memory entry."""
    TASK = "task"           # Valid for one task
    AGENT = "agent"         # Valid for one agent execution
    SESSION = "session"     # Valid for one session
    GLOBAL = "global"       # Valid globally


@dataclass
class WorkingMemoryEntry:
    """A single entry in working memory."""
    key: str
    value: Any
    scope: MemoryScope
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # Higher = more important


class WorkingMemory:
    """Stores temporary computation state and intermediate results."""

    def __init__(self):
        """Initialize working memory."""
        self.memory: dict[str, dict[str, WorkingMemoryEntry]] = {
            "task": {},
            "agent": {},
            "session": {},
            "global": {}
        }

    def store(
        self,
        key: str,
        value: Any,
        scope: MemoryScope = MemoryScope.TASK,
        metadata: Optional[dict[str, Any]] = None,
        priority: int = 0
    ) -> None:
        """
        Store a value in working memory.

        Args:
            key: Memory key
            value: Value to store
            scope: Memory scope (task, agent, session, global)
            metadata: Optional metadata
            priority: Priority (higher = more important)
        """
        entry = WorkingMemoryEntry(
            key=key,
            value=value,
            scope=scope,
            metadata=metadata or {},
            priority=priority
        )
        self.memory[scope.value][key] = entry

    def retrieve(self, key: str, scope: Optional[MemoryScope] = None) -> Optional[Any]:
        """
        Retrieve a value from working memory.

        Args:
            key: Memory key
            scope: Optional specific scope to check (if None, checks all scopes)

        Returns:
            The stored value, or None if not found
        """
        if scope:
            entry = self.memory[scope.value].get(key)
            if entry:
                entry.accessed_at = datetime.utcnow()
                return entry.value
        else:
            # Search all scopes
            for scope_dict in self.memory.values():
                if key in scope_dict:
                    entry = scope_dict[key]
                    entry.accessed_at = datetime.utcnow()
                    return entry.value

        return None

    def exists(self, key: str, scope: Optional[MemoryScope] = None) -> bool:
        """
        Check if a key exists in working memory.

        Args:
            key: Memory key
            scope: Optional specific scope to check

        Returns:
            True if key exists
        """
        if scope:
            return key in self.memory[scope.value]
        else:
            for scope_dict in self.memory.values():
                if key in scope_dict:
                    return True
            return False

    def update(self, key: str, value: Any, scope: Optional[MemoryScope] = None) -> bool:
        """
        Update a value in working memory.

        Args:
            key: Memory key
            value: New value
            scope: Optional specific scope to update

        Returns:
            True if updated, False if not found
        """
        if scope:
            if key in self.memory[scope.value]:
                entry = self.memory[scope.value][key]
                entry.value = value
                entry.accessed_at = datetime.utcnow()
                return True
        else:
            for scope_dict in self.memory.values():
                if key in scope_dict:
                    entry = scope_dict[key]
                    entry.value = value
                    entry.accessed_at = datetime.utcnow()
                    return True

        return False

    def delete(self, key: str, scope: Optional[MemoryScope] = None) -> bool:
        """
        Delete a value from working memory.

        Args:
            key: Memory key
            scope: Optional specific scope

        Returns:
            True if deleted, False if not found
        """
        if scope:
            if key in self.memory[scope.value]:
                del self.memory[scope.value][key]
                return True
        else:
            for scope_dict in self.memory.values():
                if key in scope_dict:
                    del scope_dict[key]
                    return True

        return False

    def clear_scope(self, scope: MemoryScope) -> int:
        """
        Clear all memory in a scope.

        Args:
            scope: Memory scope to clear

        Returns:
            Number of entries cleared
        """
        count = len(self.memory[scope.value])
        self.memory[scope.value] = {}
        return count

    def get_scope_contents(self, scope: MemoryScope) -> dict[str, Any]:
        """
        Get all contents of a scope.

        Args:
            scope: Memory scope

        Returns:
            Dictionary of key -> value
        """
        return {
            key: entry.value
            for key, entry in self.memory[scope.value].items()
        }

    def get_by_priority(self, scope: MemoryScope, limit: int = 10) -> list[tuple[str, Any, int]]:
        """
        Get entries from a scope sorted by priority.

        Args:
            scope: Memory scope
            limit: Maximum number of entries to return

        Returns:
            List of (key, value, priority) tuples sorted by priority
        """
        entries = self.memory[scope.value].values()
        sorted_entries = sorted(entries, key=lambda e: e.priority, reverse=True)
        return [
            (e.key, e.value, e.priority)
            for e in sorted_entries[:limit]
        ]

    def get_stats(self) -> dict[str, int]:
        """Get statistics about working memory usage."""
        return {
            scope: len(entries)
            for scope, entries in self.memory.items()
        }

