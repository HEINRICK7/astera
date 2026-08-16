"""Deterministic local analyzer for contract tests."""
from __future__ import annotations

from .models import ImageRequest, VisionResult


class DeterministicImageAnalyzer:
    """Return configured analysis while preserving the provider boundary."""

    def __init__(
        self,
        *,
        labels: tuple[str, ...] = (),
        objects: tuple[str, ...] = (),
        text: str | None = None,
        provider: str = "deterministic",
    ) -> None:
        self._labels = labels
        self._objects = objects
        self._text = text
        self._provider = provider

    async def analyze(self, request: ImageRequest) -> VisionResult:
        return VisionResult(
            request_id=request.image_id,
            provider=self._provider,
            labels=self._labels,
            objects=self._objects,
            text=self._text,
        )
