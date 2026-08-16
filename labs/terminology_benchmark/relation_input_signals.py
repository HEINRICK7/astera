"""Typed upstream contract consumed by the clinical relation boundary.

This module owns input completeness, not relation compilation.  It makes
missing ownership/state/transition evidence explicit so the compiler never
has to guess what an incomplete semantic signal means.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


RELATION_BEARING_ATTRIBUTES = frozenset({"dose", "frequency", "route", "laterality", "status"})
OWNER_REQUIRED_ATTRIBUTES = frozenset({"dose", "frequency", "route", "laterality", "status"})


class SignalState(str, Enum):
    CURRENT = "current"
    HISTORICAL = "historical"
    UNRESOLVED = "unresolved"


class SignalStatus(str, Enum):
    RESOLVED = "RESOLVED"
    UNRESOLVED_OWNER = "UNRESOLVED_OWNER"
    UNRESOLVED_STATE = "UNRESOLVED_STATE"
    AMBIGUOUS = "AMBIGUOUS"


def _sources(provenance: Mapping[str, Any]) -> tuple[str, ...]:
    values = provenance.get("source_segment_ids", ())
    return tuple(str(value) for value in values if value is not None)


@dataclass(frozen=True, slots=True)
class ResolvedAttributeSignal:
    attribute_type: str
    value: Any
    owner_mention_id: str | None
    owner_type: str | None
    state: SignalState
    provenance: Mapping[str, Any]
    confidence: float = 1.0
    evidence: tuple[str, ...] = ()
    status: SignalStatus | None = None

    def __post_init__(self) -> None:
        if not self.attribute_type:
            raise ValueError("attribute signal requires attribute_type")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("attribute signal confidence must be between 0 and 1")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "evidence", tuple(self.evidence))
        if self.status is None:
            if self.attribute_type in OWNER_REQUIRED_ATTRIBUTES and (not self.owner_mention_id or not self.owner_type):
                status = SignalStatus.UNRESOLVED_OWNER
            elif self.state is SignalState.UNRESOLVED:
                status = SignalStatus.UNRESOLVED_STATE
            elif self.value is None or not _sources(self.provenance):
                status = SignalStatus.UNRESOLVED_STATE
            else:
                status = SignalStatus.RESOLVED
            object.__setattr__(self, "status", status)

    @property
    def relation_ready(self) -> bool:
        return self.status is SignalStatus.RESOLVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "attribute_type": self.attribute_type,
            "value": self.value,
            "owner_mention_id": self.owner_mention_id,
            "owner_type": self.owner_type,
            "state": self.state.value,
            "status": self.status.value if self.status else None,
            "provenance": dict(self.provenance),
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "relation_ready": self.relation_ready,
        }


@dataclass(frozen=True, slots=True)
class ResolvedTransitionSignal:
    attribute_type: str
    owner_mention_id: str | None
    owner_type: str | None
    previous_value: Any
    current_value: Any
    transition_type: str
    temporal_anchor: Any
    provenance: Mapping[str, Any]
    state: SignalState
    confidence: float = 1.0
    status: SignalStatus | None = None

    def __post_init__(self) -> None:
        if not self.attribute_type or not self.transition_type:
            raise ValueError("transition signal requires attribute_type and transition_type")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("transition signal confidence must be between 0 and 1")
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        if self.status is None:
            if not self.owner_mention_id or not self.owner_type:
                status = SignalStatus.UNRESOLVED_OWNER
            elif self.state is SignalState.UNRESOLVED:
                status = SignalStatus.UNRESOLVED_STATE
            elif self.previous_value is None or self.current_value is None or self.previous_value == self.current_value:
                status = SignalStatus.AMBIGUOUS
            elif not _sources(self.provenance):
                status = SignalStatus.UNRESOLVED_STATE
            else:
                status = SignalStatus.RESOLVED
            object.__setattr__(self, "status", status)

    @property
    def relation_ready(self) -> bool:
        return self.status is SignalStatus.RESOLVED

    def to_dict(self) -> dict[str, Any]:
        return {
            "attribute_type": self.attribute_type,
            "owner_mention_id": self.owner_mention_id,
            "owner_type": self.owner_type,
            "previous_value": self.previous_value,
            "current_value": self.current_value,
            "transition_type": self.transition_type,
            "temporal_anchor": self.temporal_anchor,
            "state": self.state.value,
            "status": self.status.value if self.status else None,
            "provenance": dict(self.provenance),
            "confidence": self.confidence,
            "relation_ready": self.relation_ready,
        }


@dataclass(frozen=True, slots=True)
class RelationInputContractReport:
    attribute_signals: tuple[ResolvedAttributeSignal, ...]
    transition_signals: tuple[ResolvedTransitionSignal, ...]

    @property
    def all_signals(self) -> tuple[ResolvedAttributeSignal | ResolvedTransitionSignal, ...]:
        return self.attribute_signals + self.transition_signals

    @property
    def owner_completeness(self) -> float:
        required = [item for item in self.all_signals if item.attribute_type in OWNER_REQUIRED_ATTRIBUTES]
        return sum(item.status is not SignalStatus.UNRESOLVED_OWNER for item in required) / len(required) if required else 1.0

    @property
    def state_completeness(self) -> float:
        return sum(item.state is not SignalState.UNRESOLVED for item in self.all_signals) / len(self.all_signals) if self.all_signals else 1.0

    @property
    def transition_validity(self) -> float:
        if not self.transition_signals:
            return 1.0
        return sum(item.relation_ready for item in self.transition_signals) / len(self.transition_signals)

    @property
    def provenance_completeness(self) -> float:
        return sum(bool(_sources(item.provenance)) for item in self.all_signals) / len(self.all_signals) if self.all_signals else 1.0

    @property
    def has_blocking_signal(self) -> bool:
        return any(not item.relation_ready for item in self.all_signals)

    def to_dict(self) -> dict[str, Any]:
        return {
            "attribute_signals": [item.to_dict() for item in self.attribute_signals],
            "transition_signals": [item.to_dict() for item in self.transition_signals],
            "relation_input_owner_completeness": self.owner_completeness,
            "relation_input_state_completeness": self.state_completeness,
            "transition_contract_validity": self.transition_validity,
            "relation_input_provenance": self.provenance_completeness,
            "has_blocking_signal": self.has_blocking_signal,
        }
