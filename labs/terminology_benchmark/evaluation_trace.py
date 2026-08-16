"""Append-only observability contract for future clinical-semantic evaluations.

This module deliberately lives at the benchmark boundary.  It does not import
or execute the Clinical Resolver.  A future evaluator may construct a trace
while it runs, and the first-divergence analyzer can later inspect a saved
trace without loading the resolver at all.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Sequence


STAGE_ORDER: tuple[str, ...] = (
    "input_segments",
    "local_mentions",
    "semantic_candidates",
    "reference_resolution",
    "ownership_resolution",
    "cross_segment_state",
    "resolved_semantics",
    "generated_relations",
    "final_projection",
    "prediction",
    "gold",
    "comparison",
)
TRACE_GRANULARITY_V2_FIELDS: tuple[str, ...] = (
    "per_mention_attributes",
    "per_mention_relations",
    "candidate_to_resolved_field_map",
    "ownership_decisions",
    "relation_generation_inputs",
    "relation_generation_outputs",
    "projection_field_map",
    "dropped_fields_by_stage",
    "transformed_fields_by_stage",
)
TRACE_GRANULARITY_V2_STAGES = {"semantic_candidates", "reference_resolution", "ownership_resolution", "generated_relations", "final_projection"}
_STAGE_INDEX = {stage: index for index, stage in enumerate(STAGE_ORDER)}


class TraceContractError(ValueError):
    """Raised when a trace violates the append-only contract."""


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return tuple(sorted((_freeze(item) for item in value), key=repr))
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _canonical(value: Any) -> str:
    return json.dumps(
        _thaw(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def stable_hash(value: Any) -> str:
    """Return a deterministic SHA-256 for JSON-compatible data."""

    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _tuple_strings(values: Sequence[str] | None) -> tuple[str, ...]:
    return tuple(values or ())


@dataclass(frozen=True, slots=True)
class ClinicalDecisionTrace:
    """One explicit decision made while materializing a stage."""

    decision_id: str
    stage: str
    description: str
    policy_rules: tuple[str, ...] = ()
    input_hash: str | None = None
    output_hash: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.stage not in _STAGE_INDEX:
            raise TraceContractError(f"unknown decision stage: {self.stage}")
        object.__setattr__(self, "policy_rules", _tuple_strings(self.policy_rules))
        object.__setattr__(self, "provenance", _freeze(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "stage": self.stage,
            "description": self.description,
            "policy_rules": list(self.policy_rules),
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "provenance": _thaw(self.provenance),
        }


@dataclass(frozen=True, slots=True)
class ClinicalMismatchTrace:
    """A saved semantic mismatch used by the offline analyzer."""

    semantic_dimension: str
    expected: Any
    actual: Any
    stage: str
    confidence: float = 1.0
    policy_rules: tuple[str, ...] = ()
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.stage not in _STAGE_INDEX:
            raise TraceContractError(f"unknown mismatch stage: {self.stage}")
        if not 0.0 <= self.confidence <= 1.0:
            raise TraceContractError("mismatch confidence must be between 0 and 1")
        object.__setattr__(self, "policy_rules", _tuple_strings(self.policy_rules))
        object.__setattr__(self, "expected", _freeze(self.expected))
        object.__setattr__(self, "actual", _freeze(self.actual))
        object.__setattr__(self, "details", _freeze(self.details))

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_dimension": self.semantic_dimension,
            "expected": _thaw(self.expected),
            "actual": _thaw(self.actual),
            "stage": self.stage,
            "confidence": self.confidence,
            "policy_rules": list(self.policy_rules),
            "details": _thaw(self.details),
        }


@dataclass(frozen=True, slots=True)
class ClinicalStageSnapshot:
    """Immutable output of one ordered evaluation stage."""

    stage: str
    payload: Any
    input_hash: str | None = None
    decisions: tuple[ClinicalDecisionTrace, ...] = ()
    preserved_fields: tuple[str, ...] = ()
    changed_fields: tuple[str, ...] = ()
    dropped_fields: tuple[str, ...] = ()
    provenance: Mapping[str, Any] = field(default_factory=dict)
    granularity: Mapping[str, Any] = field(default_factory=dict)
    output_hash: str = field(init=False)
    chain_hash: str | None = None

    def __post_init__(self) -> None:
        if self.stage not in _STAGE_INDEX:
            raise TraceContractError(f"unknown snapshot stage: {self.stage}")
        object.__setattr__(self, "payload", _freeze(copy.deepcopy(_thaw(self.payload))))
        object.__setattr__(self, "decisions", tuple(self.decisions))
        object.__setattr__(self, "preserved_fields", _tuple_strings(self.preserved_fields))
        object.__setattr__(self, "changed_fields", _tuple_strings(self.changed_fields))
        object.__setattr__(self, "dropped_fields", _tuple_strings(self.dropped_fields))
        object.__setattr__(self, "provenance", _freeze(copy.deepcopy(_thaw(self.provenance))))
        object.__setattr__(self, "granularity", _freeze(copy.deepcopy(_thaw(self.granularity))))
        object.__setattr__(self, "output_hash", stable_hash(self.payload))

    def with_chain_hash(self, previous_chain_hash: str | None) -> "ClinicalStageSnapshot":
        chain_material = {
            "previous_chain_hash": previous_chain_hash,
            "stage": self.stage,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "decisions": [decision.to_dict() for decision in self.decisions],
            "preserved_fields": list(self.preserved_fields),
            "changed_fields": list(self.changed_fields),
            "dropped_fields": list(self.dropped_fields),
            "provenance": _thaw(self.provenance),
        }
        if self.granularity:
            chain_material["granularity"] = _thaw(self.granularity)
        return replace(self, chain_hash=stable_hash(chain_material))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "chain_hash": self.chain_hash,
            "payload": _thaw(self.payload),
            "decisions": [decision.to_dict() for decision in self.decisions],
            "preserved_fields": list(self.preserved_fields),
            "changed_fields": list(self.changed_fields),
            "dropped_fields": list(self.dropped_fields),
            "provenance": _thaw(self.provenance),
            "granularity": _thaw(self.granularity),
        }


@dataclass(frozen=True, slots=True)
class ClinicalEvaluationTrace:
    """Complete append-only trace for one evaluation case."""

    evaluation_id: str
    case_id: str
    corpus_version: str
    corpus_checksum: str
    resolver_version: str
    resolver_checksum: str
    policy_version: str
    schema_version: str = "v1"
    snapshots: tuple[ClinicalStageSnapshot, ...] = ()
    decisions: tuple[ClinicalDecisionTrace, ...] = ()
    mismatches: tuple[ClinicalMismatchTrace, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        evaluation_id: str,
        case_id: str,
        corpus_version: str,
        corpus_checksum: str,
        resolver_version: str,
        resolver_checksum: str,
        policy_version: str,
        schema_version: str = "v1",
    ) -> "ClinicalEvaluationTrace":
        return cls(
            evaluation_id=evaluation_id,
            case_id=case_id,
            corpus_version=corpus_version,
            corpus_checksum=corpus_checksum,
            resolver_version=resolver_version,
            resolver_checksum=resolver_checksum,
            policy_version=policy_version,
            schema_version=schema_version,
        )

    def append_snapshot(self, snapshot: ClinicalStageSnapshot) -> "ClinicalEvaluationTrace":
        if any(item.stage == snapshot.stage for item in self.snapshots):
            raise TraceContractError(f"stage already appended: {snapshot.stage}")
        if self.snapshots:
            previous = self.snapshots[-1]
            if _STAGE_INDEX[snapshot.stage] <= _STAGE_INDEX[previous.stage]:
                raise TraceContractError(
                    f"stage order violation: {snapshot.stage} after {previous.stage}"
                )
            expected_input = previous.output_hash
            if snapshot.input_hash is None:
                snapshot = replace(snapshot, input_hash=expected_input)
            elif snapshot.input_hash != expected_input:
                raise TraceContractError(
                    f"input hash mismatch for {snapshot.stage}: "
                    f"expected {expected_input}, got {snapshot.input_hash}"
                )
            previous_chain = previous.chain_hash
        else:
            if snapshot.input_hash is not None:
                raise TraceContractError("first stage cannot have an input hash")
            previous_chain = None
        expected_chain = snapshot.with_chain_hash(previous_chain).chain_hash
        if snapshot.chain_hash is not None and snapshot.chain_hash != expected_chain:
            raise TraceContractError(f"chain hash mismatch at {snapshot.stage}")
        snapshot = snapshot.with_chain_hash(previous_chain)
        return replace(self, snapshots=self.snapshots + (snapshot,))

    def add_decision(self, decision: ClinicalDecisionTrace) -> "ClinicalEvaluationTrace":
        if any(item.decision_id == decision.decision_id for item in self.decisions):
            raise TraceContractError(f"duplicate decision id: {decision.decision_id}")
        return replace(self, decisions=self.decisions + (decision,))

    def add_mismatch(self, mismatch: ClinicalMismatchTrace) -> "ClinicalEvaluationTrace":
        return replace(self, mismatches=self.mismatches + (mismatch,))

    def validate(self) -> dict[str, bool]:
        if not self.snapshots:
            raise TraceContractError("trace must contain at least one snapshot")
        if self.snapshots[0].stage != STAGE_ORDER[0]:
            raise TraceContractError("trace must begin with input_segments")
        self._validate_hash_chain()
        if self.schema_version == "v2":
            for snapshot in self.snapshots:
                if snapshot.stage in TRACE_GRANULARITY_V2_STAGES:
                    missing = [field for field in TRACE_GRANULARITY_V2_FIELDS if field not in snapshot.granularity]
                    if missing:
                        raise TraceContractError(
                            f"v2 granularity missing at {snapshot.stage}: {', '.join(missing)}"
                        )
        stages = {snapshot.stage for snapshot in self.snapshots}
        missing_stages = [stage for stage in STAGE_ORDER if stage not in stages]
        if missing_stages:
            raise TraceContractError(f"trace is missing stages: {', '.join(missing_stages)}")
        if "prediction" not in stages:
            raise TraceContractError("trace must preserve a prediction snapshot")
        if "gold" not in stages:
            raise TraceContractError("trace must preserve a gold snapshot")
        if len([stage for stage in stages if stage == "prediction"]) != 1:
            raise TraceContractError("prediction snapshot must be unique")
        if len([stage for stage in stages if stage == "gold"]) != 1:
            raise TraceContractError("gold snapshot must be unique")
        return {
            "trace_case_id_stable": bool(self.case_id),
            "trace_stage_order_stable": True,
            "trace_no_prediction_loss": "prediction" in stages,
            "trace_no_gold_mutation": "gold" in stages,
            "trace_provenance_complete": all(bool(snapshot.provenance) for snapshot in self.snapshots),
            "trace_hash_chain_valid": True,
        }

    def _validate_hash_chain(self) -> None:
        previous_chain: str | None = None
        previous_stage_index = -1
        for snapshot in self.snapshots:
            if _STAGE_INDEX[snapshot.stage] <= previous_stage_index:
                raise TraceContractError("snapshot stage order is not strictly increasing")
            if snapshot.chain_hash != snapshot.with_chain_hash(previous_chain).chain_hash:
                raise TraceContractError(f"hash chain mismatch at {snapshot.stage}")
            previous_chain = snapshot.chain_hash
            previous_stage_index = _STAGE_INDEX[snapshot.stage]

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_schema": f"clinical-evaluation-trace/{self.schema_version}",
            "evaluation_id": self.evaluation_id,
            "case_id": self.case_id,
            "corpus_version": self.corpus_version,
            "corpus_checksum": self.corpus_checksum,
            "resolver_version": self.resolver_version,
            "resolver_checksum": self.resolver_checksum,
            "policy_version": self.policy_version,
            "stage_order": list(STAGE_ORDER),
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
            "decisions": [decision.to_dict() for decision in self.decisions],
            "mismatches": [mismatch.to_dict() for mismatch in self.mismatches],
        }

    def to_json(self) -> str:
        data = self.to_dict()
        if self.schema_version == "v2":
            data["trace_schema"] = "clinical-evaluation-trace/v2"
        if self.schema_version == "v1":
            for snapshot in data["snapshots"]:
                snapshot.pop("granularity", None)
        return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

    def save(self, path: str | Path) -> None:
        self.validate()
        Path(path).write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ClinicalEvaluationTrace":
        trace_schema = data.get("trace_schema")
        if trace_schema not in {"clinical-evaluation-trace/v1", "clinical-evaluation-trace/v2"}:
            raise TraceContractError("unsupported trace schema")
        trace = cls.create(
            evaluation_id=data["evaluation_id"],
            case_id=data["case_id"],
            corpus_version=data["corpus_version"],
            corpus_checksum=data["corpus_checksum"],
            resolver_version=data["resolver_version"],
            resolver_checksum=data["resolver_checksum"],
            policy_version=data["policy_version"],
            schema_version="v2" if trace_schema.endswith("/v2") else "v1",
        )
        for item in data.get("snapshots", []):
            decisions = tuple(
                ClinicalDecisionTrace(
                    decision_id=decision["decision_id"],
                    stage=decision["stage"],
                    description=decision["description"],
                    policy_rules=tuple(decision.get("policy_rules", ())),
                    input_hash=decision.get("input_hash"),
                    output_hash=decision.get("output_hash"),
                    provenance=decision.get("provenance", {}),
                )
                for decision in item.get("decisions", ())
            )
            snapshot = ClinicalStageSnapshot(
                stage=item["stage"],
                payload=item.get("payload"),
                input_hash=item.get("input_hash"),
                decisions=decisions,
                preserved_fields=tuple(item.get("preserved_fields", ())),
                changed_fields=tuple(item.get("changed_fields", ())),
                dropped_fields=tuple(item.get("dropped_fields", ())),
                provenance=item.get("provenance", {}),
                granularity=item.get("granularity", {}),
            )
            if item.get("output_hash") != snapshot.output_hash:
                raise TraceContractError(f"output hash mismatch at {snapshot.stage}")
            if item.get("chain_hash") is not None:
                snapshot = replace(snapshot, chain_hash=item["chain_hash"])
            trace = trace.append_snapshot(snapshot)
        for item in data.get("decisions", ()):
            trace = trace.add_decision(ClinicalDecisionTrace(
                decision_id=item["decision_id"],
                stage=item["stage"],
                description=item["description"],
                policy_rules=tuple(item.get("policy_rules", ())),
                input_hash=item.get("input_hash"),
                output_hash=item.get("output_hash"),
                provenance=item.get("provenance", {}),
            ))
        for item in data.get("mismatches", ()):
            trace = trace.add_mismatch(ClinicalMismatchTrace(
                semantic_dimension=item["semantic_dimension"],
                expected=item.get("expected"),
                actual=item.get("actual"),
                stage=item["stage"],
                confidence=float(item.get("confidence", 1.0)),
                policy_rules=tuple(item.get("policy_rules", ())),
                details=item.get("details", {}),
            ))
        trace.validate()
        return trace

    @classmethod
    def load(cls, path: str | Path) -> "ClinicalEvaluationTrace":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _diff_values(expected: Any, actual: Any, path: str = "") -> list[dict[str, Any]]:
    if isinstance(expected, Mapping) and isinstance(actual, Mapping):
        differences: list[dict[str, Any]] = []
        for key in sorted(set(expected) | set(actual)):
            child = f"{path}.{key}" if path else str(key)
            differences.extend(_diff_values(expected.get(key), actual.get(key), child))
        return differences
    if isinstance(expected, list) and isinstance(actual, list):
        differences = []
        for index in range(max(len(expected), len(actual))):
            child = f"{path}[{index}]"
            differences.extend(_diff_values(
                expected[index] if index < len(expected) else None,
                actual[index] if index < len(actual) else None,
                child,
            ))
        return differences
    if expected != actual:
        return [{"semantic_dimension": path or "root", "expected": expected, "actual": actual}]
    return []


def _semantic_view(payload: Any) -> Any:
    """Strip evaluation metadata before fallback prediction/gold comparison."""
    if not isinstance(payload, Mapping) or not isinstance(payload.get("mentions"), list):
        return payload
    mentions = []
    for mention in payload["mentions"]:
        if not isinstance(mention, Mapping):
            mentions.append(mention)
            continue
        relations = []
        for relation in mention.get("relations", []):
            if isinstance(relation, Mapping):
                relations.append({
                    "relation_type": relation.get("relation_type"),
                    "target": relation.get("target"),
                    "value": relation.get("value"),
                })
            else:
                relations.append(relation)
        mentions.append({
            "surface": mention.get("surface"),
            "fields": mention.get("fields", {}),
            "relations": relations,
        })
    return {"mentions": mentions}


class FirstDivergenceAnalyzer:
    """Analyze saved traces and never invoke a live resolver."""

    def analyze(
        self,
        trace: ClinicalEvaluationTrace,
        gold: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace.validate()
        mismatches = list(trace.mismatches)
        inferred = False
        if not mismatches:
            gold_payload = gold
            if gold_payload is None:
                gold_snapshot = next(snapshot for snapshot in trace.snapshots if snapshot.stage == "gold")
                gold_payload = _thaw(gold_snapshot.payload)
            prediction = next(snapshot for snapshot in trace.snapshots if snapshot.stage == "prediction")
            mismatches = [ClinicalMismatchTrace(
                semantic_dimension=item["semantic_dimension"],
                expected=item["expected"],
                actual=item["actual"],
                stage="prediction",
                confidence=0.5,
                details={"inferred_from_saved_prediction": True},
            ) for item in _diff_values(_semantic_view(gold_payload), _semantic_view(_thaw(prediction.payload)))]
            inferred = bool(mismatches)
        mismatches.sort(key=lambda item: (_STAGE_INDEX[item.stage], item.semantic_dimension))
        if not mismatches:
            return {
                "status": "PASS",
                "evaluation_id": trace.evaluation_id,
                "case_id": trace.case_id,
                "first_divergence_stage": None,
                "semantic_dimension": None,
                "expected": None,
                "actual": None,
                "upstream_state": [],
                "downstream_effects": [],
                "confidence": 1.0,
                "mismatches": [],
                "inferred": False,
            }
        first = mismatches[0]
        first_index = _STAGE_INDEX[first.stage]
        upstream = [
            {"stage": snapshot.stage, "output_hash": snapshot.output_hash}
            for snapshot in trace.snapshots
            if _STAGE_INDEX[snapshot.stage] <= first_index
        ]
        downstream = [
            {
                "stage": snapshot.stage,
                "changed_fields": list(snapshot.changed_fields),
                "dropped_fields": list(snapshot.dropped_fields),
            }
            for snapshot in trace.snapshots
            if _STAGE_INDEX[snapshot.stage] > first_index
            and (snapshot.changed_fields or snapshot.dropped_fields)
        ]
        return {
            "status": "FAIL",
            "evaluation_id": trace.evaluation_id,
            "case_id": trace.case_id,
            "first_divergence_stage": first.stage,
            "semantic_dimension": first.semantic_dimension,
            "expected": _thaw(first.expected),
            "actual": _thaw(first.actual),
            "upstream_state": upstream,
            "downstream_effects": downstream,
            "confidence": first.confidence,
            "policy_rules": list(first.policy_rules),
            "mismatches": [item.to_dict() for item in mismatches],
            "inferred": inferred,
        }


def analyze_saved_trace(path: str | Path, gold: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Load and analyze one saved trace without importing the resolver."""

    return FirstDivergenceAnalyzer().analyze(ClinicalEvaluationTrace.load(path), gold)
