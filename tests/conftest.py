"""Pytest configuration and fixtures."""

import pytest
from app.config import Settings
from app.kernel.registry import Registry
from app.providers import OllamaProvider
from app.router import ModelRouter
from app.workflow import WorkflowEngine
from app.memory import ConversationMemory


@pytest.fixture
def settings():
    """Get test settings."""
    return Settings(
        ollama_url="http://localhost:11434",
        ollama_model="qwen2.5-coder:7b",
        log_level="DEBUG"
    )


@pytest.fixture
def registry():
    """Get a fresh registry."""
    return Registry()


@pytest.fixture
def ollama_provider(settings):
    """Get an Ollama provider."""
    return OllamaProvider(
        base_url=settings.ollama_url,
        model=settings.ollama_model
    )


@pytest.fixture
def model_router(ollama_provider):
    """Get a model router."""
    router = ModelRouter(default_provider=ollama_provider)
    return router


@pytest.fixture
def workflow_engine(registry, model_router):
    """Get a workflow engine."""
    return WorkflowEngine(registry, model_router)


@pytest.fixture
def conversation_memory():
    """Get conversation memory."""
    return ConversationMemory()

