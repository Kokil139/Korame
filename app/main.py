"""
Korame V1 - Main FastAPI Application.

AI-native software factory with multi-agent orchestration.
"""

import sys
import asyncio

if sys.platform == "win32":
    # The Testing agent's sandbox runs pytest via asyncio.create_subprocess_exec().
    # On Windows, that raises a bare NotImplementedError (no message at all) if
    # the Selector event loop is active instead of Proactor - which is exactly
    # what surfaced as an unexplained, empty "Error:" during the testing phase,
    # with nothing useful in the logs either since the exception has no message.
    # Set this as early as possible (before uvicorn creates the event loop).
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.utils import logger, setup_logging
from app.kernel import Registry
from app.providers import OllamaProvider
from app.router import ModelRouter
from app.agents import RTEAgent, DeveloperAgent, TestingAgent
from app.workflow import WorkflowEngine
from app.knowledge import KnowledgeFabric
from app.integrations import GitHubService
from app.api import (
    router,
    set_engine,
    set_memory,
    development_router,
    set_development_engine,
    set_development_memory,
    set_development_story_run_store,
)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app
    """
    # Setup logging
    setup_logging()
    logger.info("Starting Korame V1")

    # Get settings
    settings = get_settings()

    # Initialize core components
    registry = Registry()
    model_router = ModelRouter()
    workflow_engine = WorkflowEngine(registry, model_router)

    # Initialize Knowledge Fabric. Its conversation_memory is used as THE
    # conversation store (single source of truth) so agents can also use the
    # fabric's search/artifact APIs against the same data.
    knowledge_fabric = KnowledgeFabric()
    conversation_memory = knowledge_fabric.conversation_memory
    logger.info("Initialized Knowledge Fabric")

    # Register providers
    ollama_provider = OllamaProvider(
        base_url=settings.ollama_url,
        model=settings.ollama_model
    )
    registry.register_provider(ollama_provider)
    model_router.set_default_provider(ollama_provider)
    logger.info(f"Registered Ollama provider: {settings.ollama_model}")

    # Register agents
    rte_agent = RTEAgent(model_router=model_router, knowledge_fabric=knowledge_fabric)
    registry.register_agent(rte_agent)
    logger.info("Registered RTE agent")

    # Developer/Testing agents share the same qwen3:8b model via model_router
    # for now (see docs/ARCHITECTURE.md); GitHub PR creation is skipped
    # gracefully if GITHUB_TOKEN/GITHUB_REPO aren't set in .env.
    github_service = GitHubService(
        token=settings.github_token,
        repo=settings.github_repo,
        base_branch=settings.github_base_branch,
    )
    developer_agent = DeveloperAgent(
        model_router=model_router,
        todo_store=knowledge_fabric.todo_store,
        github_service=github_service,
    )
    registry.register_agent(developer_agent)
    logger.info(
        "Registered Developer agent (GitHub PRs %s)"
        % ("enabled" if github_service.is_configured() else "not configured")
    )

    testing_agent = TestingAgent(model_router=model_router)
    registry.register_agent(testing_agent)
    logger.info("Registered Testing agent")

    # Set up API dependencies
    set_engine(workflow_engine)
    set_memory(conversation_memory)
    set_development_engine(workflow_engine)
    set_development_memory(conversation_memory)
    set_development_story_run_store(knowledge_fabric.story_run_store)
    logger.info("Initialized workflow engine and conversation memory")

    # Create FastAPI app
    app = FastAPI(
        title="Korame V1",
        description="AI-native software factory with multi-agent orchestration",
        version="0.1.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(router)
    app.include_router(development_router)

    logger.info(f"Korame V1 ready on {settings.api_host}:{settings.api_port}")

    return app


# Create the application
app = create_app()


@app.on_event("startup")
async def startup_event() -> None:
    """Called when the app starts."""
    logger.info("Korame startup complete")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Called when the app shuts down."""
    logger.info("Korame shutdown")


if __name__ == "__main__":
    import uvicorn
    from app.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

