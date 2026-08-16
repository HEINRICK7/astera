"""Representation engine port."""
from __future__ import annotations

from typing import Protocol

from .models import RepresentationRequest, RepresentationResult


class RepresentationEngine(Protocol):
    async def render(self, request: RepresentationRequest) -> RepresentationResult:
        """Render knowledge without changing its source record."""
