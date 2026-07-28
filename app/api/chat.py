"""
API endpoints for Korame.

Provides REST interface for executing workflows and managing conversations.
"""

from typing import Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/v1", tags=["korame"])

# Request/Response models
class ChatRequest(BaseModel):
    """Request to chat with an agent."""
    agent_name: str
    requirement: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from an agent."""
    task_id: str
    conversation_id: str
    agent_name: str
    status: str
    user_story: Optional[str] = None
    needs_clarification: bool = False
    questions: list[str] = []
    suggestions: list[str] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# Global state (will be injected via dependency injection)
_workflow_engine = None
_conversation_memory = None


def set_engine(engine: Any) -> None:
    """Set the workflow engine."""
    global _workflow_engine
    _workflow_engine = engine


def set_memory(memory: Any) -> None:
    """Set the conversation memory."""
    global _conversation_memory
    _conversation_memory = memory


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(status="ok", version="0.1.0")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Execute a workflow task (e.g., RTE requirement to user story).

    Args:
        request: Chat request with agent name and requirement

    Returns:
        Chat response with generated user story

    Raises:
        HTTPException: If the request fails
    """
    if not _workflow_engine:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")

    if not _conversation_memory:
        raise HTTPException(status_code=500, detail="Conversation memory not initialized")

    try:
        # Generate IDs
        task_id = str(uuid.uuid4())
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Ensure conversation exists
        _conversation_memory.start_conversation(conversation_id)

        # Capture prior turns BEFORE adding the new message, so the agent can
        # use them as context without seeing the current message twice.
        history = _conversation_memory.get_context_for_model(conversation_id)

        # Add user message to memory
        _conversation_memory.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.requirement,
            agent_name=request.agent_name,
            task_id=task_id
        )

        # Execute the workflow, passing prior turns so the agent can ask
        # clarifying questions with full context of what was already discussed
        response = await _workflow_engine.execute(
            agent_name=request.agent_name,
            input_data={
                "requirement": request.requirement,
                "history": history,
                "conversation_id": conversation_id,
            },
            task_id=task_id
        )

        # Add agent response to memory
        if response.status == "success":
            user_story = response.data.get("user_story", "")
            needs_clarification = response.data.get("needs_clarification", False)
            questions = response.data.get("questions", [])
            suggestions = response.data.get("suggestions", [])
            _conversation_memory.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=user_story,
                agent_name=request.agent_name,
                task_id=task_id
            )

            return ChatResponse(
                task_id=task_id,
                conversation_id=conversation_id,
                agent_name=request.agent_name,
                status="success",
                user_story=user_story,
                needs_clarification=needs_clarification,
                questions=questions,
                suggestions=suggestions
            )
        else:
            error_msg = response.error or "Unknown error"
            _conversation_memory.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=f"Error: {error_msg}",
                agent_name=request.agent_name,
                task_id=task_id
            )

            return ChatResponse(
                task_id=task_id,
                conversation_id=conversation_id,
                agent_name=request.agent_name,
                status="error",
                error=error_msg
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations() -> dict[str, Any]:
    """
    List all known conversations with a short preview, for building a
    "past conversations" list in the frontend.

    Returns:
        List of conversation summaries (id, preview, message count, last update)
    """
    if not _conversation_memory:
        raise HTTPException(status_code=500, detail="Conversation memory not initialized")

    summaries = []
    for conversation_id in _conversation_memory.list_conversations():
        messages = _conversation_memory.get_conversation(conversation_id)
        if not messages:
            continue

        first_user_message = next((m for m in messages if m.role == "user"), None)
        last_message = messages[-1]

        summaries.append({
            "conversation_id": conversation_id,
            "preview": (first_user_message.content[:120] if first_user_message else ""),
            "message_count": len(messages),
            "updated_at": last_message.timestamp.isoformat()
        })

    summaries.sort(key=lambda s: s["updated_at"], reverse=True)
    return {"conversations": summaries}


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict[str, Any]:
    """
    Get a conversation history.

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation history
    """
    if not _conversation_memory:
        raise HTTPException(status_code=500, detail="Conversation memory not initialized")

    messages = _conversation_memory.get_conversation(conversation_id)
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "agent_name": m.agent_name,
                "timestamp": m.timestamp.isoformat()
            }
            for m in messages
        ]
    }

