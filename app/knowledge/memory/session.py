"""
Session memory for Korame.

Stores session-level state and user context.
"""

from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionContext:
    """Session context information."""
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)


class SessionMemory:
    """Stores session-level state and user context."""

    def __init__(self, session_ttl_seconds: int = 3600):
        """
        Initialize session memory.

        Args:
            session_ttl_seconds: How long before sessions expire (default: 1 hour)
        """
        self.sessions: dict[str, SessionContext] = {}
        self.session_ttl_seconds = session_ttl_seconds

    def create_session(
        self,
        session_id: str,
        user_id: str,
        metadata: Optional[dict[str, Any]] = None
    ) -> SessionContext:
        """
        Create a new session.

        Args:
            session_id: Unique session ID
            user_id: User ID
            metadata: Optional metadata

        Returns:
            The created session context
        """
        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get a session.

        Args:
            session_id: Session ID

        Returns:
            The session context, or None if not found or expired
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check if expired
        elapsed = (datetime.utcnow() - session.created_at).total_seconds()
        if elapsed > self.session_ttl_seconds:
            del self.sessions[session_id]
            return None

        # Update last activity
        session.last_activity = datetime.utcnow()
        return session

    def set_variable(self, session_id: str, key: str, value: Any) -> bool:
        """
        Set a variable in a session.

        Args:
            session_id: Session ID
            key: Variable key
            value: Variable value

        Returns:
            True if set, False if session not found
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.variables[key] = value
        session.last_activity = datetime.utcnow()
        return True

    def get_variable(self, session_id: str, key: str) -> Optional[Any]:
        """
        Get a variable from a session.

        Args:
            session_id: Session ID
            key: Variable key

        Returns:
            The variable value, or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        return session.variables.get(key)

    def get_variables(self, session_id: str) -> dict[str, Any]:
        """
        Get all variables from a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary of variables
        """
        session = self.get_session(session_id)
        if not session:
            return {}

        return session.variables.copy()

    def delete_variable(self, session_id: str, key: str) -> bool:
        """
        Delete a variable from a session.

        Args:
            session_id: Session ID
            key: Variable key

        Returns:
            True if deleted, False if not found
        """
        session = self.get_session(session_id)
        if not session or key not in session.variables:
            return False

        del session.variables[key]
        session.last_activity = datetime.utcnow()
        return True

    def end_session(self, session_id: str) -> bool:
        """
        End a session.

        Args:
            session_id: Session ID

        Returns:
            True if ended, False if not found
        """
        if session_id not in self.sessions:
            return False

        del self.sessions[session_id]
        return True

    def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions removed
        """
        now = datetime.utcnow()
        expired_ids = []

        for session_id, session in self.sessions.items():
            elapsed = (now - session.created_at).total_seconds()
            if elapsed > self.session_ttl_seconds:
                expired_ids.append(session_id)

        for session_id in expired_ids:
            del self.sessions[session_id]

        return len(expired_ids)

    def list_sessions(self) -> list[str]:
        """Get list of active session IDs."""
        self.cleanup_expired()
        return list(self.sessions.keys())

