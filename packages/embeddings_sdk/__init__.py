"""Provider-neutral contracts for Astera embedding generation."""

from .in_memory import DeterministicEmbedder
from .models import EmbeddingRequest, EmbeddingResult, EmbeddingVector
from .protocol import Embedder

__all__ = ["DeterministicEmbedder", "Embedder", "EmbeddingRequest", "EmbeddingResult", "EmbeddingVector"]
