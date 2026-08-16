"""Immutable OCR contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class OcrRequest:
    document_id: str
    content: bytes
    mime_type: str = "application/pdf"
    language: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError("document_id must not be empty")
        if not self.content:
            raise ValueError("content must not be empty")
        if not self.mime_type.strip():
            raise ValueError("mime_type must not be empty")


@dataclass(frozen=True, slots=True)
class OcrBlock:
    text: str
    page: int = 1
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("text must not be empty")
        if self.page < 1:
            raise ValueError("page must be at least 1")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class OcrResult:
    request_id: str
    provider: str
    blocks: tuple[OcrBlock, ...]
    language: str | None = None

    @property
    def text(self) -> str:
        return "\n".join(block.text for block in self.blocks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "language": self.language,
            "text": self.text,
            "blocks": [
                {
                    "text": block.text,
                    "page": block.page,
                    "confidence": block.confidence,
                }
                for block in self.blocks
            ],
        }
