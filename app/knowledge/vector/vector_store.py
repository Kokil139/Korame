"""
Vector storage for Korame.

Stores embeddings and enables similarity search.
Uses in-memory storage by default; integrate with Qdrant/Pinecone for production.
"""

from typing import Optional, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import math


@dataclass
class VectorEntry:
    """A vector stored in the vector database."""
    entry_id: str
    vector: List[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    text: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryVectorStore:
    """
    In-memory vector storage with cosine similarity search.

    For production, consider:
    - Qdrant: pip install qdrant-client
    - Pinecone: pip install pinecone-client
    - Weaviate: pip install weaviate-client
    - Milvus: pip install pymilvus
    """

    def __init__(self, vector_dimension: int = 768):
        """
        Initialize vector store.

        Args:
            vector_dimension: Dimension of vectors (e.g., 768 for sentence-transformers)
        """
        self.vector_dimension = vector_dimension
        self.vectors: dict[str, VectorEntry] = {}

    def add(
        self,
        entry_id: str,
        vector: List[float],
        text: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> bool:
        """
        Add a vector to the store.

        Args:
            entry_id: Unique ID for this vector
            vector: Vector embedding (list of floats)
            text: Optional source text
            metadata: Optional metadata

        Returns:
            True if added, False if dimensions don't match
        """
        if len(vector) != self.vector_dimension:
            return False

        entry = VectorEntry(
            entry_id=entry_id,
            vector=vector,
            text=text,
            metadata=metadata or {}
        )
        self.vectors[entry_id] = entry
        return True

    def get(self, entry_id: str) -> Optional[VectorEntry]:
        """Get a vector entry by ID."""
        return self.vectors.get(entry_id)

    def search(
        self,
        query_vector: List[float],
        k: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            k: Number of results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (entry_id, similarity_score) tuples sorted by similarity
        """
        if len(query_vector) != self.vector_dimension:
            return []

        similarities = []

        for entry_id, entry in self.vectors.items():
            similarity = self._cosine_similarity(query_vector, entry.vector)
            if similarity >= threshold:
                similarities.append((entry_id, similarity))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]

    def delete(self, entry_id: str) -> bool:
        """Delete a vector entry."""
        if entry_id in self.vectors:
            del self.vectors[entry_id]
            return True
        return False

    def clear(self) -> int:
        """Clear all vectors. Returns number of entries cleared."""
        count = len(self.vectors)
        self.vectors = {}
        return count

    def size(self) -> int:
        """Get number of vectors stored."""
        return len(self.vectors)

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_vectors": len(self.vectors),
            "vector_dimension": self.vector_dimension,
            "memory_usage_approx_mb": (len(self.vectors) * self.vector_dimension * 8) / (1024 * 1024)
        }

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        # Avoid division by zero
        if mag1 == 0 or mag2 == 0:
            return 0.0

        # Return cosine similarity
        return dot_product / (mag1 * mag2)


class LlamaIndexVectorStore:
    """
    Vector storage backed by LlamaIndex's ``SimpleVectorStore``.

    Exposes the same ``add`` / ``search`` / ``delete`` / ``clear`` interface as
    ``InMemoryVectorStore`` so it can be used as a drop-in replacement anywhere
    that class appears.

    Requires: pip install llama-index-core
    """

    def __init__(self, vector_dimension: int = 768):
        from llama_index.core.vector_stores import SimpleVectorStore
        self.vector_dimension = vector_dimension
        self._store = SimpleVectorStore()
        self._count: int = 0

    def add(
        self,
        entry_id: str,
        vector: List[float],
        text: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        if len(vector) != self.vector_dimension:
            return False
        from llama_index.core.schema import TextNode
        node = TextNode(
            id_=entry_id,
            text=text or "",
            metadata=metadata or {},
            embedding=list(vector),
        )
        self._store.add([node])
        self._count += 1
        return True

    def search(
        self,
        query_vector: List[float],
        k: int = 10,
        threshold: float = 0.5,
    ) -> List[Tuple[str, float]]:
        if len(query_vector) != self.vector_dimension:
            return []
        from llama_index.core.vector_stores import VectorStoreQuery
        query = VectorStoreQuery(query_embedding=list(query_vector), similarity_top_k=k)
        result = self._store.query(query)
        out: List[Tuple[str, float]] = []
        for node_id, score in zip(result.ids or [], result.similarities or []):
            if float(score) >= threshold:
                out.append((node_id, float(score)))
        return out

    def get(self, entry_id: str) -> Optional[VectorEntry]:
        """Not directly supported by SimpleVectorStore — always returns None."""
        return None

    def delete(self, entry_id: str) -> bool:
        self._store.delete(entry_id)
        self._count = max(0, self._count - 1)
        return True

    def clear(self) -> int:
        from llama_index.core.vector_stores import SimpleVectorStore
        count = self._count
        self._store = SimpleVectorStore()
        self._count = 0
        return count

    def size(self) -> int:
        return self._count

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_vectors": self._count,
            "vector_dimension": self.vector_dimension,
            "backend": "llama_index.SimpleVectorStore",
        }


    @staticmethod
    def _euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))


# External Vector Store Integrations
VECTOR_STORE_OPTIONS = """
# Vector Store Options

## In-Memory (V1)
- Fast for development
- Limited to single machine
- No persistence

## Qdrant (Recommended)
```bash
pip install qdrant-client
docker run -p 6333:6333 qdrant/qdrant
```

## Pinecone
```bash
pip install pinecone-client
```

## Weaviate
```bash
pip install weaviate-client
docker run -p 8080:8080 semitechnologies/weaviate:latest
```

## Milvus
```bash
pip install pymilvus
docker run -d --name milvus -p 19530:19530 milvusdb/milvus:latest
```
"""

