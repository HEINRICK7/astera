"""Immutable terminology lookup contracts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TerminologyQuery:
    system: str
    code: str | None = None
    text: str | None = None
    version: str | None = None

    def __post_init__(self) -> None:
        if not self.system.strip():
            raise ValueError("system must not be empty")
        if not (self.code and self.code.strip()) and not (self.text and self.text.strip()):
            raise ValueError("code or text must be provided")


@dataclass(frozen=True, slots=True)
class TerminologyConcept:
    system: str
    code: str
    display: str
    version: str | None = None
    active: bool = True

    def __post_init__(self) -> None:
        if not self.system.strip() or not self.code.strip() or not self.display.strip():
            raise ValueError("system, code and display must not be empty")


@dataclass(frozen=True, slots=True)
class TerminologyResult:
    query: TerminologyQuery
    provider: str
    concepts: tuple[TerminologyConcept, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "query": {
                "system": self.query.system,
                "code": self.query.code,
                "text": self.query.text,
                "version": self.query.version,
            },
            "concepts": [
                {
                    "system": concept.system,
                    "code": concept.code,
                    "display": concept.display,
                    "version": concept.version,
                    "active": concept.active,
                }
                for concept in self.concepts
            ],
        }
