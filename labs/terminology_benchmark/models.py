"""Benchmark-only data contracts and result models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class GoldMention:
    surface: str
    concept_id: str
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
    occurrence: int = 0
    relations: tuple["GoldRelation", ...] = ()
    segment_ids: tuple[str, ...] = ()
    attribute_provenance: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    relation_provenance: Mapping[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GoldRelation:
    relation_type: str
    target: str
    value: str | None = None


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    case_id: str
    text: str
    language: str
    gold: tuple[GoldMention, ...]
    source: str = "niede-pt-br-v1"
    segments: tuple["ConversationSegment", ...] = ()


@dataclass(frozen=True, slots=True)
class ConversationSegment:
    segment_id: str
    speaker: str
    text: str


@dataclass(frozen=True, slots=True)
class BenchmarkAnnotation:
    surface: str
    concept_id: str
    start: int
    end: int
    score: float | None = None
    semantic_types: tuple[str, ...] = ()
    negated: bool | None = None
    certainty: str | None = None
    temporality: str | None = None
    experiencer: str | None = None
    laterality: str | None = None
    dose: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ProviderMetadata:
    provider: str
    code_license: str
    data_license: str
    model_license: str
    vocabulary: str
    vocabulary_version: str
    source_uri: str
    model_path: str | None = None
    asset_bytes: int | None = None
    asset_sha256: str | None = None
    notes: str = ""


@dataclass(frozen=True, slots=True)
class BenchmarkReport:
    provider: ProviderMetadata
    cases: int
    entity_precision: float
    entity_recall: float
    linking_accuracy: float
    false_positive_rate: float
    attribute_accuracy: Mapping[str, float]
    provenance_completeness: float
    concept_stability: float
    latency_ms: Mapping[str, float]
    cpu_seconds: float
    rss_bytes: int
    startup_seconds: float
    weighted_score: float
    hard_gate_passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider.provider,
            "metadata": {
                "code_license": self.provider.code_license,
                "data_license": self.provider.data_license,
                "model_license": self.provider.model_license,
                "vocabulary": self.provider.vocabulary,
                "vocabulary_version": self.provider.vocabulary_version,
                "source_uri": self.provider.source_uri,
                "model_path": self.provider.model_path,
                "asset_bytes": self.provider.asset_bytes,
                "asset_sha256": self.provider.asset_sha256,
                "notes": self.provider.notes,
            },
            "cases": self.cases,
            "metrics": {
                "entity_precision": self.entity_precision,
                "entity_recall": self.entity_recall,
                "linking_accuracy": self.linking_accuracy,
                "false_positive_rate": self.false_positive_rate,
                "attribute_accuracy": dict(self.attribute_accuracy),
                "provenance_completeness": self.provenance_completeness,
                "concept_stability": self.concept_stability,
                "latency_ms": dict(self.latency_ms),
                "cpu_seconds": self.cpu_seconds,
                "rss_bytes": self.rss_bytes,
                "startup_seconds": self.startup_seconds,
            },
            "weighted_score": self.weighted_score,
            "hard_gate_passed": self.hard_gate_passed,
        }
