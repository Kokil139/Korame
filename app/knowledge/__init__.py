"""
Korame Knowledge Fabric.

Central system for storing and managing:
- Conversation memory (user-agent interactions)
- Agent memory (agent-specific state)
- Session memory (session-level context)
- Working memory (temporary computation)
- Knowledge graph (entity relationships)
- Vector store (embeddings for RAG)
- Full-text search
- Semantic search
- Hybrid search
- Artifact storage (with versioning)
"""

from app.knowledge.memory import (
    ConversationMemory,
    ConversationMessage,
    AgentMemory,
    AgentMemoryEntry,
    SessionMemory,
    SessionContext,
    WorkingMemory,
    WorkingMemoryEntry,
    MemoryScope
)
from app.knowledge.graph import (
    NetworkXGraph,
    GraphNode,
    GraphEdge,
    Neo4jGraph
)
from app.knowledge.vector import (
    InMemoryVectorStore,
    VectorEntry
)
from app.knowledge.embeddings import (
    EmbeddingProvider,
    SentenceTransformersEmbedding,
    OpenAIEmbedding,
    DummyEmbedding
)
from app.knowledge.search import (
    SearchType,
    SearchResult,
    FullTextSearch,
    SemanticSearch,
    HybridSearch
)
from app.knowledge.artifacts import (
    ArtifactType,
    ArtifactStatus,
    Artifact,
    ArtifactVersion,
    ArtifactStore
)
from app.knowledge.knowledge_service import KnowledgeFabric

__all__ = [
    # Memory
    "ConversationMemory",
    "ConversationMessage",
    "AgentMemory",
    "AgentMemoryEntry",
    "SessionMemory",
    "SessionContext",
    "WorkingMemory",
    "WorkingMemoryEntry",
    "MemoryScope",
    # Graph
    "NetworkXGraph",
    "GraphNode",
    "GraphEdge",
    "Neo4jGraph",
    # Vector
    "InMemoryVectorStore",
    "VectorEntry",
    # Embeddings
    "EmbeddingProvider",
    "SentenceTransformersEmbedding",
    "OpenAIEmbedding",
    "DummyEmbedding",
    # Search
    "SearchType",
    "SearchResult",
    "FullTextSearch",
    "SemanticSearch",
    "HybridSearch",
    # Artifacts
    "ArtifactType",
    "ArtifactStatus",
    "Artifact",
    "ArtifactVersion",
    "ArtifactStore",
    # Service
    "KnowledgeFabric"
]

