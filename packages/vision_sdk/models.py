"""Immutable image analysis contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ImageRequest:
    image_id: str
    image: bytes
    mime_type: str = "image/png"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.image_id.strip():
            raise ValueError("image_id must not be empty")
        if not self.image:
            raise ValueError("image must not be empty")
        if not self.mime_type.strip():
            raise ValueError("mime_type must not be empty")


@dataclass(frozen=True, slots=True)
class VisionResult:
    request_id: str
    provider: str
    labels: tuple[str, ...] = ()
    objects: tuple[str, ...] = ()
    text: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "labels": list(self.labels),
            "objects": list(self.objects),
            "text": self.text,
            "metadata": dict(self.metadata),
        }
