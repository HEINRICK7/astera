"""Clinical representation boundary."""
from __future__ import annotations

from packages.representation_sdk import RepresentationEngine, RepresentationRequest, RepresentationResult


class ClinicalRepresentationModule:
    def __init__(self, engine: RepresentationEngine) -> None:
        self._engine = engine

    async def render(self, request: RepresentationRequest) -> RepresentationResult:
        return await self._engine.render(request)
