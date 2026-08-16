"""Provider-neutral Knowledge and Research outbound boundaries.

These contracts deliberately describe derived results. They never expose a
vendor SDK, HTTP client, database model or mutable canonical evidence object.
Adapters such as terminology services or external research providers will be
added in a later milestone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable


def _required(value: str, name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value.strip()


@dataclass(frozen=True, slots=True)
class KnowledgeLookupQuery:
    """A provider-neutral request for clinical concept knowledge."""

    concept: str
    context: Mapping[str, str] = field(default_factory=dict)
    terminology_system: str | None = None
    as_of: str | None = None

    def __post_init__(self) -> None:
        _required(self.concept, "concept")
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))


@dataclass(frozen=True, slots=True)
class KnowledgeConcept:
    """A derived concept returned by a Knowledge provider."""

    concept_id: str
    display: str
    semantic_type: str
    code: str | None = None
    system: str | None = None

    def __post_init__(self) -> None:
        _required(self.concept_id, "concept_id")
        _required(self.display, "display")
        _required(self.semantic_type, "semantic_type")


@dataclass(frozen=True, slots=True)
class KnowledgeResult:
    """Immutable, derived knowledge enrichment with provider provenance."""

    query: KnowledgeLookupQuery
    provider: str
    concepts: tuple[KnowledgeConcept, ...] = ()
    related_concept_ids: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required(self.provider, "provider")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@dataclass(frozen=True, slots=True)
class ClinicalQuestion:
    """Provider-neutral question submitted to Research."""

    question: str
    encounter_id: str | None = None
    context_id: str | None = None
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _required(self.question, "question")


@dataclass(frozen=True, slots=True)
class ResearchFinding:
    """An externally retrieved, derived finding; never canonical evidence."""

    finding_id: str
    title: str
    summary: str
    source_uri: str | None = None
    source_type: str = "unknown"

    def __post_init__(self) -> None:
        _required(self.finding_id, "finding_id")
        _required(self.title, "title")
        _required(self.summary, "summary")
        _required(self.source_type, "source_type")


@dataclass(frozen=True, slots=True)
class ResearchResult:
    """Immutable research output and provenance."""

    result_id: str
    question: ClinicalQuestion
    provider: str
    findings: tuple[ResearchFinding, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required(self.result_id, "result_id")
        _required(self.provider, "provider")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@runtime_checkable
class KnowledgePort(Protocol):
    """Application boundary for terminology/knowledge enrichment."""

    async def lookup(self, query: KnowledgeLookupQuery) -> KnowledgeResult:
        ...


@runtime_checkable
class ResearchPort(Protocol):
    """Application boundary for external clinical research retrieval."""

    async def search(self, question: ClinicalQuestion) -> ResearchResult:
        ...

