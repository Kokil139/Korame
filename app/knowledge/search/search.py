"""
Search functionality for Korame.

Full-text search, semantic search, and hybrid search capabilities.
"""

from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from enum import Enum


class SearchType(str, Enum):
    """Types of search."""
    FULL_TEXT = "full_text"      # Keyword matching
    SEMANTIC = "semantic"         # Embedding-based similarity
    HYBRID = "hybrid"             # Combination of both


@dataclass
class SearchResult:
    """A search result."""
    artifact_id: str
    title: str
    description: str
    score: float  # 0-1, higher is better
    search_type: SearchType
    metadata: dict[str, Any]


class FullTextSearch:
    """
    Simple full-text search using keyword matching.

    For production, consider Elasticsearch or Solr.
    """

    def __init__(self):
        """Initialize full-text search."""
        self.index: Dict[str, List[Dict[str, Any]]] = {}  # keyword -> [documents]

    def index_document(
        self,
        doc_id: str,
        title: str,
        description: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Index a document for full-text search.

        Args:
            doc_id: Unique document ID
            title: Document title
            description: Document description
            content: Document content
            metadata: Optional metadata
        """
        # Combine all text and tokenize
        full_text = f"{title} {description} {content}".lower()
        keywords = self._tokenize(full_text)

        for keyword in keywords:
            if keyword not in self.index:
                self.index[keyword] = []

            self.index[keyword].append({
                "doc_id": doc_id,
                "title": title,
                "description": description,
                "metadata": metadata or {}
            })

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search documents by keywords.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of search results
        """
        query_keywords = self._tokenize(query.lower())

        # Find documents matching any keyword
        doc_scores: Dict[str, float] = {}
        docs: Dict[str, Dict[str, Any]] = {}

        for keyword in query_keywords:
            if keyword in self.index:
                for doc in self.index[keyword]:
                    doc_id = doc["doc_id"]
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = 0
                        docs[doc_id] = doc

                    # Score increases with more keyword matches
                    doc_scores[doc_id] += 1

        # Normalize scores
        if doc_scores:
            max_score = max(doc_scores.values())
            doc_scores = {k: v / max_score for k, v in doc_scores.items()}

        # Sort by score
        sorted_docs = sorted(
            [(doc_id, score) for doc_id, score in doc_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )

        # Create results
        results = []
        for doc_id, score in sorted_docs[:limit]:
            doc = docs[doc_id]
            results.append(SearchResult(
                artifact_id=doc_id,
                title=doc["title"],
                description=doc["description"],
                score=score,
                search_type=SearchType.FULL_TEXT,
                metadata=doc["metadata"]
            ))

        return results

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple tokenization (split on whitespace and punctuation)."""
        import re
        # Split on whitespace and punctuation
        tokens = re.findall(r'\w+', text)
        # Filter out very short tokens
        return [t for t in tokens if len(t) > 2]


class SemanticSearch:
    """
    Semantic search using embeddings.

    Requires a vector store and embedding provider.
    """

    def __init__(self, vector_store, embedding_provider):
        """
        Initialize semantic search.

        Args:
            vector_store: Vector store instance
            embedding_provider: Embedding provider instance
        """
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.document_index: Dict[str, Dict[str, Any]] = {}

    def index_document(
        self,
        doc_id: str,
        title: str,
        description: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Index a document for semantic search.

        Args:
            doc_id: Unique document ID
            title: Document title
            description: Document description
            content: Document content
            metadata: Optional metadata
        """
        # Combine text and generate embedding
        text_to_embed = f"{title} {description} {content}"
        embedding = self.embedding_provider.embed_text(text_to_embed)

        # Store in vector store
        self.vector_store.add(
            entry_id=doc_id,
            vector=embedding,
            text=text_to_embed,
            metadata=metadata or {}
        )

        # Store document info
        self.document_index[doc_id] = {
            "title": title,
            "description": description,
            "metadata": metadata or {}
        }

    def search(self, query: str, limit: int = 10, threshold: float = 0.5) -> List[SearchResult]:
        """
        Search documents by semantic similarity.

        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity score

        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self.embedding_provider.embed_text(query)

        # Search in vector store
        similar_docs = self.vector_store.search(
            query_vector=query_embedding,
            k=limit,
            threshold=threshold
        )

        # Create results
        results = []
        for doc_id, score in similar_docs:
            if doc_id in self.document_index:
                doc = self.document_index[doc_id]
                results.append(SearchResult(
                    artifact_id=doc_id,
                    title=doc["title"],
                    description=doc["description"],
                    score=score,
                    search_type=SearchType.SEMANTIC,
                    metadata=doc["metadata"]
                ))

        return results


class HybridSearch:
    """
    Hybrid search combining full-text and semantic search.
    """

    def __init__(self, full_text_search, semantic_search):
        """
        Initialize hybrid search.

        Args:
            full_text_search: FullTextSearch instance
            semantic_search: SemanticSearch instance
        """
        self.full_text_search = full_text_search
        self.semantic_search = semantic_search

    def search(
        self,
        query: str,
        limit: int = 10,
        full_text_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[SearchResult]:
        """
        Hybrid search combining both methods.

        Args:
            query: Search query
            limit: Maximum number of results
            full_text_weight: Weight for full-text results (0-1)
            semantic_weight: Weight for semantic results (0-1)

        Returns:
            List of search results sorted by combined score
        """
        # Get results from both search methods
        ft_results = self.full_text_search.search(query, limit=limit * 2)
        sem_results = self.semantic_search.search(query, limit=limit * 2)

        # Combine results
        combined: Dict[str, SearchResult] = {}

        for result in ft_results:
            result.score *= full_text_weight
            combined[result.artifact_id] = result

        for result in sem_results:
            if result.artifact_id in combined:
                # Combine scores
                existing = combined[result.artifact_id]
                combined[result.artifact_id].score = (
                    existing.score + (result.score * semantic_weight)
                ) / 2
            else:
                result.score *= semantic_weight
                combined[result.artifact_id] = result

        # Sort by combined score
        results = sorted(
            combined.values(),
            key=lambda r: r.score,
            reverse=True
        )

        return results[:limit]

