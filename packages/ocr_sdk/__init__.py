"""Provider-neutral contracts for Astera OCR capabilities."""

from .in_memory import DeterministicOcrEngine
from .models import OcrBlock, OcrRequest, OcrResult
from .protocol import OcrEngine

__all__ = ["DeterministicOcrEngine", "OcrBlock", "OcrEngine", "OcrRequest", "OcrResult"]
