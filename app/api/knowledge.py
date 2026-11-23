"""
API endpoints for the Knowledge Agent.

Lets the floating "Knowledge Assistant" widget ask questions that get
answered by searching the Knowledge Fabric's indexed application documents.
"""

from typing import Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

# Global state (injected via dependency injection, same pattern as app/api/chat.py)
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

class AskRequest(BaseModel):
    """A question for the Knowledge Agent."""
    question: str
    conversation_id: Optional[str] = None

class SourceRef(BaseModel):
    """A single cited excerpt the answer was grounded in."""
    source: str
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    score: float = 0.0

class AskResponse(BaseModel):
    """Response from the Knowledge Agent."""
    task_id: str
    conversation_id: str
    status: str
    answer: Optional[str] = None
    sources: list[SourceRef] = []
    found_context: bool = False
    error: Optional[str] = None

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """
    Ask the Knowledge Agent a question about the application's indexed documents.

    Args:
        request: The question, plus an optional conversation_id to continue
                 a prior exchange with follow-up context.

    Returns:
        The grounded answer and the sources it was based on.

    Raises:
        HTTPException: If the request fails.
    """
    if not _workflow_engine:
        raise HTTPException(status_code=500, detail="Workflow engine not initialized")
    if not _conversation_memory:
        raise HTTPException(status_code=500, detail="Conversation memory not initialized")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    try:
        task_id = str(uuid.uuid4())
        conversation_id = request.conversation_id or str(uuid.uuid4())

        _conversation_memory.start_conversation(conversation_id)
        history = _conversation_memory.get_context_for_model(conversation_id)

        _conversation_memory.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.question,
            agent_name="knowledge",
            task_id=task_id,
        )

        response = await _workflow_engine.execute(
            agent_name="knowledge",
            input_data={
                "question": request.question,
                "history": history,
                "conversation_id": conversation_id,
            },
            task_id=task_id,
        )

        if response.status == "success":
            answer = response.data.get("answer", "")
            _conversation_memory.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
                agent_name="knowledge",
                task_id=task_id,
            )
            return AskResponse(
                task_id=task_id,
                conversation_id=conversation_id,
                status="success",
                answer=answer,
                sources=response.data.get("sources", []),
                found_context=response.data.get("found_context", False),
            )

        error_msg = response.error or "Unknown error"
        _conversation_memory.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=f"Error: {error_msg}",
            agent_name="knowledge",
            task_id=task_id,
        )
        return AskResponse(
            task_id=task_id,
            conversation_id=conversation_id,
            status="error",
            error=error_msg,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))