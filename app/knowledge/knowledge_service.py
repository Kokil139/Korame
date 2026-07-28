"""
Knowledge Fabric Service for Korame.

Central service that orchestrates memory, graph, vector store, and search.
"""

from typing import Optional, Any, List, Dict
from app.knowledge.memory import (
    ConversationMemory,
    AgentMemory,
    SessionMemory,
    WorkingMemory,
    MemoryScope
)
from app.knowledge.graph import NetworkXGraph
from app.knowledge.vector import InMemoryVectorStore
from app.knowledge.search import FullTextSearch, SemanticSearch, HybridSearch
from app.knowledge.artifacts import ArtifactStore, ArtifactType, ArtifactStatus
from app.knowledge.embeddings.embeddings import EmbeddingProvider, DummyEmbedding


class KnowledgeFabric:
    """
    Central knowledge fabric service.

    Manages:
    - Conversation memory (user-agent interactions)
    - Agent memory (agent-specific state)
    - Session memory (session-level context)
    - Working memory (temporary computation)
    - Knowledge graph (entity relationships)
    - Vector store (embeddings for RAG)
    - Search (full-text, semantic, hybrid)
    - Artifact store (software engineering artifacts)
    """

    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        vector_dimension: int = 768
    ):
        """
        Initialize the knowledge fabric.

        Args:
            embedding_provider: Custom embedding provider (defaults to DummyEmbedding)
            vector_dimension: Dimension of embeddings
        """
        # Memory systems
        self.conversation_memory = ConversationMemory()
        self.agent_memory = AgentMemory()
        self.session_memory = SessionMemory()
        self.working_memory = WorkingMemory()

        # Graph
        self.graph = NetworkXGraph()

        # Vector store
        self.vector_store = InMemoryVectorStore(vector_dimension=vector_dimension)

        # Embeddings
        self.embedding_provider = embedding_provider or DummyEmbedding(dimension=vector_dimension)

        # Search
        self.full_text_search = FullTextSearch()
        self.semantic_search = SemanticSearch(self.vector_store, self.embedding_provider)
        self.hybrid_search = HybridSearch(self.full_text_search, self.semantic_search)

        # Artifacts
        self.artifact_store = ArtifactStore()

    # ============================================================================
    # Memory APIs
    # ============================================================================

    def store_conversation(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store a conversation message."""
        self.conversation_memory.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            task_id=task_id,
            metadata=metadata
        )

    def store_agent_memory(
        self,
        agent_name: str,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """Store agent-specific state."""
        self.agent_memory.store(
            agent_name=agent_name,
            key=key,
            value=value,
            ttl_seconds=ttl_seconds
        )

    def retrieve_agent_memory(self, agent_name: str, key: str) -> Optional[Any]:
        """Retrieve agent-specific state."""
        return self.agent_memory.retrieve(agent_name, key)

    def create_session(
        self,
        session_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a new session."""
        self.session_memory.create_session(session_id, user_id, metadata)

    def set_working_memory(
        self,
        key: str,
        value: Any,
        scope: MemoryScope = MemoryScope.TASK
    ) -> None:
        """Store temporary computation state."""
        self.working_memory.store(key, value, scope=scope)

    def get_working_memory(self, key: str) -> Optional[Any]:
        """Retrieve temporary computation state."""
        return self.working_memory.retrieve(key)

    # ============================================================================
    # Graph APIs
    # ============================================================================

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add an entity to the knowledge graph."""
        self.graph.add_node(entity_id, entity_type, properties)

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add a relationship between entities."""
        return self.graph.add_edge(
            source_id,
            target_id,
            relationship_type,
            properties
        )

    def get_related_entities(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        """Get entities related to a given entity."""
        nodes = self.graph.get_related_nodes(entity_id, relationship_type, max_depth)
        return [
            {
                "id": n.node_id,
                "type": n.label,
                "properties": n.properties
            }
            for n in nodes
        ]

    # ============================================================================
    # Search APIs
    # ============================================================================

    def index_for_search(
        self,
        doc_id: str,
        title: str,
        description: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Index a document for search (both full-text and semantic)."""
        self.full_text_search.index_document(doc_id, title, description, content, metadata)
        self.semantic_search.index_document(doc_id, title, description, content, metadata)

    def search(
        self,
        query: str,
        search_type: str = "hybrid",
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            search_type: "full_text", "semantic", or "hybrid"
            limit: Maximum results
            threshold: Minimum similarity score

        Returns:
            List of search results
        """
        if search_type == "full_text":
            results = self.full_text_search.search(query, limit)
        elif search_type == "semantic":
            results = self.semantic_search.search(query, limit, threshold)
        else:  # hybrid
            results = self.hybrid_search.search(query, limit)

        return [
            {
                "artifact_id": r.artifact_id,
                "title": r.title,
                "description": r.description,
                "score": r.score,
                "type": r.search_type.value,
                "metadata": r.metadata
            }
            for r in results
        ]

    # ============================================================================
    # Artifact APIs
    # ============================================================================

    def create_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        title: str,
        description: str,
        created_by: str,
        content: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new artifact."""
        artifact = self.artifact_store.create_artifact(
            artifact_id=artifact_id,
            artifact_type=ArtifactType[artifact_type.upper()],
            title=title,
            description=description,
            created_by=created_by,
            content=content,
            metadata=metadata
        )

        # Index for search
        self.index_for_search(
            doc_id=artifact_id,
            title=title,
            description=description,
            content=content
        )

        # Add to graph
        self.add_entity(artifact_id, artifact_type, {"title": title})

        return {
            "artifact_id": artifact.artifact_id,
            "type": artifact.artifact_type.value,
            "status": artifact.status.value,
            "title": artifact.title
        }

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get an artifact."""
        artifact = self.artifact_store.get_artifact(artifact_id)
        if not artifact:
            return None

        return {
            "artifact_id": artifact.artifact_id,
            "type": artifact.artifact_type.value,
            "title": artifact.title,
            "description": artifact.description,
            "status": artifact.status.value,
            "content": artifact.content,
            "created_by": artifact.created_by,
            "created_at": artifact.created_at.isoformat(),
            "updated_at": artifact.updated_at.isoformat(),
            "versions": len(artifact.versions),
            "tags": artifact.tags,
            "related": artifact.related_artifacts
        }

    def update_artifact(
        self,
        artifact_id: str,
        content: str,
        author: str,
        change_summary: str = ""
    ) -> bool:
        """Update an artifact."""
        success = self.artifact_store.update_artifact(
            artifact_id=artifact_id,
            content=content,
            author=author,
            change_summary=change_summary
        )

        if success:
            # Re-index for search
            artifact = self.artifact_store.get_artifact(artifact_id)
            if artifact:
                self.index_for_search(
                    doc_id=artifact_id,
                    title=artifact.title,
                    description=artifact.description,
                    content=content
                )

        return success

    # ============================================================================
    # Stats and Health
    # ============================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge fabric."""
        return {
            "artifacts": self.artifact_store.get_stats(),
            "graph": self.graph.get_stats(),
            "vector_store": self.vector_store.get_stats(),
            "working_memory": self.working_memory.get_stats(),
            "sessions": len(self.session_memory.list_sessions()),
            "agent_memory_agents": len(self.agent_memory.list_agents())
        }

    def health_check(self) -> Dict[str, bool]:
        """Check if all knowledge systems are healthy."""
        return {
            "conversation_memory": True,
            "agent_memory": True,
            "session_memory": True,
            "working_memory": True,
            "graph": len(self.graph.nodes) >= 0,
            "vector_store": True,
            "search": True,
            "artifacts": True
        }

