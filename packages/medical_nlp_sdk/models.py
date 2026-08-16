"""Immutable contracts for clinical text processing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class NlpRequest:
    request_id: str
    text: str
    language: str = "pt-BR"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.request_id.strip():
            raise ValueError("request_id must not be empty")
        if not self.text.strip():
            raise ValueError("text must not be empty")
        if not self.language.strip():
            raise ValueError("language must not be empty")


@dataclass(frozen=True, slots=True)
class ClinicalEntity:
    text: str
    label: str
    start: int
    end: int
    negated: bool = False
    assertion: str = "present"

    def __post_init__(self) -> None:
        if not self.text.strip() or not self.label.strip():
            raise ValueError("entity text and label must not be empty")
        if self.start < 0 or self.end <= self.start:
            raise ValueError("entity offsets must be ordered")


@dataclass(frozen=True, slots=True)
class NlpResult:
    request_id: str
    provider: str
    entities: tuple[ClinicalEntity, ...] = ()
    language: str = "pt-BR"

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "language": self.language,
            "entities": [
                {
                    "text": entity.text,
                    "label": entity.label,
                    "start": entity.start,
                    "end": entity.end,
                    "negated": entity.negated,
                    "assertion": entity.assertion,
                }
                for entity in self.entities
            ],
        }
