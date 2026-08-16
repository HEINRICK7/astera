"""Knowledge consolidation port."""
from __future__ import annotations

from typing import Protocol

from packages.understanding_sdk import UnderstandingSnapshot

from .models import KnowledgeRecord


class KnowledgeEngine(Protocol):
    async def consolidate(self, snapshot: UnderstandingSnapshot) -> KnowledgeRecord:
        """Consolidate provisional understanding into versioned knowledge."""
