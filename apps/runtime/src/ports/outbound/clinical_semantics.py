"""Provider-neutral ports for terminology linking and clinical context."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping, Protocol, runtime_checkable

from packages.clinical_context_sdk import ClinicalContext
from packages.clinical_facts_sdk import ClinicalFactsBatch
from packages.terminology_sdk import TerminologyQuery, TerminologyResult


@runtime_checkable
class TerminologyPort(Protocol):
    """Resolve text/codes into terminology concepts.

    The result is the existing immutable ``packages.terminology_sdk``
    contract. QuickUMLS, MedCAT and other providers will implement this port
    through adapters in a later benchmark milestone.
    """

    async def lookup(self, query: TerminologyQuery) -> TerminologyResult:
        ...


@runtime_checkable
class ClinicalContextPort(Protocol):
    """Resolve assertion context for one canonical clinical mention."""

    async def analyze(self, query: "ClinicalContextQuery") -> "ClinicalContextResult":
        ...


@dataclass(frozen=True, slots=True)
class ClinicalContextQuery:
    """Provider-neutral input for negation/temporality/experiencer analysis."""

    text: str
    language: str = "pt-BR"
    start: int = 0
    end: int | None = None
    concept_id: str | None = None
    evidence_id: str | None = None
    semantic_policy: str | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("context query text must not be empty")
        if self.start < 0 or (self.end is not None and self.end < self.start):
            raise ValueError("context query span must be ordered")


@dataclass(frozen=True, slots=True)
class ClinicalContextResult:
    """Immutable derived context attributes; never canonical evidence."""

    negated: bool = False
    certainty: str = "confirmed"
    temporality: str = "current"
    experiencer: str = "patient"
    laterality: str | None = None
    dose: str | None = None
    dose_value: str | None = None
    dose_unit: str | None = None
    frequency: str | None = None
    route: str | None = None
    status: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))


@runtime_checkable
class ClinicalContextBuilderPort(Protocol):
    """Build a versioned clinical state from canonical facts."""

    async def build(
        self,
        *,
        facts: ClinicalFactsBatch,
        previous: ClinicalContext | None = None,
        occurred_at: datetime | None = None,
    ) -> ClinicalContext:
        ...
