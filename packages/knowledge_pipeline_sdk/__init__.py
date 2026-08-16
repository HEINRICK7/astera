"""Provider-neutral contracts for the Astera Knowledge Pipeline."""

from .in_memory import SnapshotKnowledgeEngine
from .models import KnowledgeRecord
from .protocol import KnowledgeEngine

__all__ = ["KnowledgeEngine", "KnowledgeRecord", "SnapshotKnowledgeEngine"]
