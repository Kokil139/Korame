"""
Korame V1 - Main FastAPI Application.

AI-native software factory with multi-agent orchestration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.utils import logger, setup_logging
from app.kernel import Registry
from app.providers import OllamaProvider
from app.router import ModelRouter
from app.agents import RTEAgent
from app.workflow import WorkflowEngine
from app.knowledge.memory import ConversationMemory
from app.knowledge import KnowledgeFabric
from app.api import router, set_engine, set_memory


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
    conversation_memory = ConversationMemory()

    # Initialize Knowledge Fabric
    knowledge_fabric = KnowledgeFabric()
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
    rte_agent = RTEAgent(model_router=model_router)
    registry.register_agent(rte_agent)
    logger.info("Registered RTE agent")

    # Set up API dependencies
    set_engine(workflow_engine)
    set_memory(conversation_memory)
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

