"""
Embedding generation for Korame.

Converts text to vectors for similarity search and RAG.
"""

from typing import List, Optional, Union
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        pass


class SentenceTransformersEmbedding(EmbeddingProvider):
    """
    Embedding using Sentence Transformers.

    Requires: pip install sentence-transformers

    Usage:
        embedder = SentenceTransformersEmbedding("all-MiniLM-L6-v2")
        embedding = embedder.embed_text("Hello world")
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a Sentence Transformers model.

        Args:
            model_name: Model name (e.g., "all-MiniLM-L6-v2", "all-mpnet-base-v2")
        """
        self.model_name = model_name
        self.model = None
        self.dimension = None

    def _load_model(self):
        """Lazily load the model on first use."""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                # Get dimension from model
                self.dimension = self.model.get_sentence_embedding_dimension()
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        if self.model is None:
            self._load_model()
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        if self.model is None:
            self._load_model()
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        if self.dimension is None:
            self._load_model()
        return self.dimension


class OpenAIEmbedding(EmbeddingProvider):
    """
    Embedding using OpenAI API.

    Requires: pip install openai

    Usage:
        embedder = OpenAIEmbedding(api_key="sk-...")
        embedding = embedder.embed_text("Hello world")
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize with OpenAI API key.

        Args:
            api_key: OpenAI API key
            model: Model name (text-embedding-3-small or text-embedding-3-large)
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        self.dimension = None

    def _init_client(self):
        """Lazily initialize OpenAI client."""
        if self.client is None:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.dimension = 1536 if self.model == "text-embedding-3-small" else 3072
            except ImportError:
                raise ImportError(
                    "openai not installed. "
                    "Install with: pip install openai"
                )

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        if self.client is None:
            self._init_client()

        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings."""
        if self.client is None:
            self._init_client()

        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        if self.dimension is None:
            self._init_client()
        return self.dimension


class DummyEmbedding(EmbeddingProvider):
    """
    Dummy embedding provider for testing.

    Returns random vectors - useful for testing without external dependencies.
    """

    def __init__(self, dimension: int = 768):
        """
        Initialize with vector dimension.

        Args:
            dimension: Embedding dimension (default: 768)
        """
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Return a random vector."""
        import random
        return [random.random() for _ in range(self.dimension)]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return random vectors."""
        import random
        return [[random.random() for _ in range(self.dimension)] for _ in texts]

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.dimension


# Embedding model recommendations
EMBEDDING_MODELS = """
# Embedding Models

## Sentence Transformers (Recommended for V1)
- Local, fast, no API key needed
- Good quality for general use
- Models: all-MiniLM-L6-v2, all-mpnet-base-v2

## OpenAI
- High quality
- Requires API key
- Models: text-embedding-3-small, text-embedding-3-large

## Ollama
- Local, open source
- Integration coming

## Cohere
- High quality
- Requires API key

## HuggingFace
- Many open models
- Local or via API
"""

