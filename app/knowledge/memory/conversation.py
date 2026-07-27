"""
Conversation memory for Korame.

Stores message history between users and agents.
"""

from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ConversationMessage:
    """A single message in a conversation."""
    role: str  # "user", "assistant", "agent"
    content: str
    agent_name: Optional[str] = None
    task_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ConversationMemory:
    """Stores conversation history between users and agents."""

    def __init__(self):
        """Initialize conversation memory."""
        self.conversations: dict[str, list[ConversationMessage]] = {}

    def start_conversation(self, conversation_id: str) -> None:
        """
        Start a new conversation.

        Args:
            conversation_id: Unique ID for this conversation
        """
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Add a message to the conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, agent)
            content: Message content
            agent_name: Optional agent name
            task_id: Optional task ID
            metadata: Optional metadata
        """
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)

        message = ConversationMessage(
            role=role,
            content=content,
            agent_name=agent_name,
            task_id=task_id,
            metadata=metadata or {}
        )
        self.conversations[conversation_id].append(message)

    def get_conversation(self, conversation_id: str) -> list[ConversationMessage]:
        """
        Get all messages in a conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            List of messages
        """
        return self.conversations.get(conversation_id, [])

    def get_context_for_model(self, conversation_id: str, max_messages: int = 10) -> str:
        """
        Get conversation context formatted for model input.

        Args:
            conversation_id: Conversation ID
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted conversation context
        """
        messages = self.get_conversation(conversation_id)
        if not messages:
            return ""

        # Get the most recent max_messages
        recent = messages[-max_messages:]

        context_lines = []
        for msg in recent:
            role = msg.role.upper()
            context_lines.append(f"{role}: {msg.content}")

        return "\n".join(context_lines)

    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear a conversation.

        Args:
            conversation_id: Conversation ID
        """
        if conversation_id in self.conversations:
            self.conversations[conversation_id] = []

    def list_conversations(self) -> list[str]:
        """Get list of all conversation IDs."""
        return list(self.conversations.keys())

