from __future__ import annotations

import json

import pytest

from labs.terminology_benchmark.evaluation_trace import (
    ClinicalDecisionTrace,
    ClinicalEvaluationTrace,
    ClinicalMismatchTrace,
    ClinicalStageSnapshot,
    FirstDivergenceAnalyzer,
    TraceContractError,
    TRACE_GRANULARITY_V2_FIELDS,
    STAGE_ORDER,
)


def _trace(*, mismatch: ClinicalMismatchTrace | None = None) -> ClinicalEvaluationTrace:
    trace = ClinicalEvaluationTrace.create(
        evaluation_id="diagnostic-d1",
        case_id="D1-001",
        corpus_version="d1-v1",
        corpus_checksum="corpus-sha",
        resolver_version="resolver-frozen",
        resolver_checksum="resolver-sha",
        policy_version="1.3",
    )
    payloads = {
        "input_segments": {"segments": [{"segment_id": "s1", "text": "dor no joelho esquerdo"}]},
        "local_mentions": {"mentions": [{"mention_id": "m1", "surface": "dor"}]},
        "semantic_candidates": {"m1": {"concept_id": "symptom.pain"}},
        "reference_resolution": {"m1": {"antecedent": "m1"}},
        "ownership_resolution": {"m1": {"laterality": "left"}},
        "cross_segment_state": {"active_mentions": ["m1"]},
        "resolved_semantics": {"m1": {"laterality": "left"}},
        "generated_relations": {"relations": [{"type": "HAS_LATERALITY", "target": "m1"}]},
        "final_projection": {"mentions": [{"mention_id": "m1", "laterality": "left"}]},
        "prediction": {"mentions": [{"mention_id": "m1", "laterality": "left"}]},
        "gold": {"mentions": [{"mention_id": "m1", "laterality": "left"}]},
        "comparison": {"status": "PASS" if mismatch is None else "FAIL"},
    }
    for stage in payloads:
        trace = trace.append_snapshot(ClinicalStageSnapshot(stage=stage, payload=payloads[stage], provenance={"segment_ids": ["s1"]}))
    if mismatch is not None:
        trace = trace.add_mismatch(mismatch)
    return trace


@pytest.mark.parametrize(
    ("stage", "dimension"),
    [
        ("local_mentions", "mention_presence"),
        ("reference_resolution", "antecedent"),
        ("ownership_resolution", "laterality"),
        ("cross_segment_state", "temporality"),
        ("generated_relations", "HAS_DOSE"),
    ],
)
def test_analyzer_reports_first_saved_divergence(stage: str, dimension: str) -> None:
    mismatch = ClinicalMismatchTrace(
        semantic_dimension=dimension,
        expected="expected",
        actual="actual",
        stage=stage,
        policy_rules=("SEM-TEST-001",),
    )
    result = FirstDivergenceAnalyzer().analyze(_trace(mismatch=mismatch))
    assert result["status"] == "FAIL"
    assert result["first_divergence_stage"] == stage
    assert result["semantic_dimension"] == dimension
    assert result["inferred"] is False
    assert result["policy_rules"] == ["SEM-TEST-001"]


def test_projection_preserved_is_a_pass() -> None:
    result = FirstDivergenceAnalyzer().analyze(_trace())
    assert result["status"] == "PASS"
    assert result["first_divergence_stage"] is None


def test_trace_is_deterministic_append_only_and_hash_protected(tmp_path) -> None:
    trace = _trace()
    first_json = trace.to_json()
    second_json = trace.to_json()
    assert first_json == second_json
    trace.validate()
    path = tmp_path / "trace.json"
    trace.save(path)
    assert ClinicalEvaluationTrace.load(path).to_json() == first_json

    tampered = json.loads(first_json)
    tampered["snapshots"][3]["payload"]["m1"]["antecedent"] = "m2"
    with pytest.raises(TraceContractError):
        ClinicalEvaluationTrace.from_dict(tampered)


def test_duplicate_or_out_of_order_stage_is_rejected() -> None:
    trace = ClinicalEvaluationTrace.create(
        evaluation_id="e", case_id="c", corpus_version="d1", corpus_checksum="c",
        resolver_version="r", resolver_checksum="r", policy_version="1.3",
    )
    trace = trace.append_snapshot(ClinicalStageSnapshot(stage="input_segments", payload={}))
    with pytest.raises(TraceContractError):
        trace.append_snapshot(ClinicalStageSnapshot(stage="input_segments", payload={}))
    with pytest.raises(TraceContractError):
        trace.append_snapshot(ClinicalStageSnapshot(stage="local_mentions", payload={}))
        trace.append_snapshot(ClinicalStageSnapshot(stage="input_segments", payload={}))


def test_gold_and_prediction_are_required_for_valid_saved_trace() -> None:
    trace = ClinicalEvaluationTrace.create(
        evaluation_id="e", case_id="c", corpus_version="d1", corpus_checksum="c",
        resolver_version="r", resolver_checksum="r", policy_version="1.3",
    ).append_snapshot(ClinicalStageSnapshot(stage="input_segments", payload={}))
    with pytest.raises(TraceContractError):
        trace.validate()


def test_complete_trace_requires_provenance_for_each_stage() -> None:
    trace = _trace()
    missing = trace.snapshots[4]
    trace = ClinicalEvaluationTrace(
        evaluation_id=trace.evaluation_id,
        case_id=trace.case_id,
        corpus_version=trace.corpus_version,
        corpus_checksum=trace.corpus_checksum,
        resolver_version=trace.resolver_version,
        resolver_checksum=trace.resolver_checksum,
        policy_version=trace.policy_version,
        snapshots=trace.snapshots[:4] + (ClinicalStageSnapshot(
            stage=missing.stage,
            payload=missing.payload,
            input_hash=missing.input_hash,
            provenance={},
        ),) + trace.snapshots[5:],
    )
    with pytest.raises(TraceContractError):
        trace.validate()


def test_trace_v2_requires_granularity_and_round_trips() -> None:
    trace = ClinicalEvaluationTrace.create(
        evaluation_id="e-v2", case_id="c-v2", corpus_version="d1", corpus_checksum="c",
        resolver_version="r", resolver_checksum="r", policy_version="1.3", schema_version="v2",
    )
    granularity = {field: {"synthetic": True} for field in TRACE_GRANULARITY_V2_FIELDS}
    for stage in STAGE_ORDER:
        trace = trace.append_snapshot(ClinicalStageSnapshot(
            stage=stage,
            payload={"stage": stage},
            provenance={"source": "synthetic-v2"},
            granularity=granularity if stage in {"semantic_candidates", "reference_resolution", "ownership_resolution", "generated_relations", "final_projection"} else {},
        ))
    trace.validate()
    encoded = trace.to_json()
    assert '"trace_schema": "clinical-evaluation-trace/v2"' in encoded
    loaded = ClinicalEvaluationTrace.from_dict(json.loads(encoded))
    assert loaded.schema_version == "v2"
    assert loaded.snapshots[7].granularity["relation_generation_outputs"]["synthetic"] is True
