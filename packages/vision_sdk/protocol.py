"""Vision provider port."""
from __future__ import annotations

from typing import Protocol

from .models import ImageRequest, VisionResult


class ImageAnalyzer(Protocol):
    async def analyze(self, request: ImageRequest) -> VisionResult:
        """Analyze an image without exposing model-specific APIs."""
