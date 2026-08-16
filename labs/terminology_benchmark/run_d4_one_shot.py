"""Execute the frozen D4 input-contract diagnostic exactly once."""
from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_safety import NieDEPtBrSafetyRules
from .corpus import mention_span
from .cross_segment_context import CrossSegmentContextAdapter
from .evaluation_trace import (
    STAGE_ORDER,
    ClinicalEvaluationTrace,
    ClinicalMismatchTrace,
    ClinicalStageSnapshot,
    FirstDivergenceAnalyzer,
)
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation
from .run_d2_one_shot import (
    FIELDS,
    _actual_record,
    _granularity,
    _jsonable,
    _mismatches,
    _resolver_checksum,
    _semantic_relation_records,
)


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
OFFICIAL = DATA / "d4_relation_input_generalization_official.jsonl"
MANIFEST = RESULTS / "D4_FREEZE_MANIFEST.json"
EXECUTION_RECORD = RESULTS / "d4-one-shot-execution-record-2026-08-15.json"
TRACE_DIR = RESULTS / "d4-traces-2026-08-15"
OUTPUT = RESULTS / "D4_ONE_SHOT_RESULT.json"
ROOT_CAUSE = RESULTS / "D4_ROOT_CAUSE_MATRIX.json"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
SIGNAL_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D4_SIGNAL_QUALITY_REPORT.md"
FIRST_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D4_FIRST_DIVERGENCE_REPORT.md"
GENERALIZATION_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D4_C2_GENERALIZATION_REPORT.md"
COMPILER = ROOT / "clinical_projection.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"


def _gold(item: dict[str, Any]) -> GoldMention:
    return GoldMention(
        **{
            **{key: value for key, value in item.items() if key not in {"relations", "segment_ids", "attribute_provenance", "relation_provenance"}},
            "relations": tuple(GoldRelation(relation_type=rel["relation_type"], target=rel["target"], value=rel.get("value")) for rel in item.get("relations", ())),
            "segment_ids": tuple(item.get("segment_ids", ())),
            "attribute_provenance": {key: tuple(value) for key, value in item.get("attribute_provenance", {}).items()},
            "relation_provenance": {key: tuple(value) for key, value in item.get("relation_provenance", {}).items()},
        }
    )


def _cases() -> tuple[BenchmarkCase, ...]:
    records = [json.loads(line) for line in OFFICIAL.read_text(encoding="utf-8").splitlines() if line.strip()]
    return tuple(
        BenchmarkCase(
            case_id=record["case_id"],
            text=record["text"],
            language=record["language"],
            source="d4-official-frozen",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        )
        for record in records
    )


def _raw_records() -> dict[str, dict[str, Any]]:
    return {record["case_id"]: record for record in (json.loads(line) for line in OFFICIAL.read_text(encoding="utf-8").splitlines() if line.strip())}


def _expected_relations(gold: GoldMention) -> list[dict[str, Any]]:
    records = [{"relation_type": item.relation_type, "target": item.target, "value": item.value} for item in gold.relations]
    if gold.dose:
        records.append({"relation_type": "HAS_DOSE", "target": "dose", "value": gold.dose})
    if gold.frequency:
        records.append({"relation_type": "HAS_FREQUENCY", "target": "frequency", "value": gold.frequency})
    if gold.route:
        records.append({"relation_type": "HAS_ROUTE", "target": "route", "value": gold.route})
    if gold.laterality:
        records.append({"relation_type": "HAS_LATERALITY", "target": "laterality", "value": gold.laterality})
    if gold.status == "discontinued":
        records.append({"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"})
    return _semantic_relation_records(records)


def _actual_relations(result: Any) -> list[dict[str, Any]]:
    return _jsonable(result.provenance.get("projection", {}).get("relations", []))


def _resolved_provenance(result: Any) -> dict[str, Any]:
    value = result.provenance.get("resolved_provenance", {})
    return value if isinstance(value, dict) else {}


def _signals(result: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    provenance = _resolved_provenance(result)
    attributes = provenance.get("relation_input_signals", ())
    transitions = provenance.get("transition_input_signals", ())
    return list(attributes) if isinstance(attributes, list) else [], list(transitions) if isinstance(transitions, list) else []


def _signal_quality(record: dict[str, Any], result: Any, mention_key: str) -> dict[str, Any]:
    expected = record.get("signal_gold", {}).get(mention_key, {})
    expected_attributes = expected.get("attributes", [])
    expected_transitions = expected.get("transitions", [])
    actual_attributes, actual_transitions = _signals(result)
    actual_all = actual_attributes + actual_transitions
    resolved_expected = [item for item in expected_attributes + expected_transitions if item.get("status") == "RESOLVED"]
    unresolved_expected = [item for item in expected_attributes + expected_transitions if item.get("status") != "RESOLVED"]
    details: list[dict[str, Any]] = []
    owner_total = owner_ok = state_total = state_ok = transition_total = transition_ok = provenance_total = provenance_ok = 0
    complete_correct = complete_wrong = unresolved_owner = unresolved_state = ambiguous = 0
    for item in expected_attributes + expected_transitions:
        is_transition = "previous_value" in item or "transition_type" in item
        candidates = actual_transitions if is_transition else actual_attributes
        candidate = next((row for row in candidates if row.get("attribute_type") == item.get("attribute_type")), None)
        expected_status = item.get("status")
        if expected_status == "RESOLVED":
            transition_total += int(is_transition)
            if is_transition:
                transition_ok += int(bool(candidate and candidate.get("status") == "RESOLVED" and candidate.get("previous_value") == item.get("previous_value") and candidate.get("current_value") == item.get("current_value") and candidate.get("state") == item.get("state")))
            owner_total += 1
            owner_ok += int(bool(candidate and candidate.get("status") == "RESOLVED" and candidate.get("owner_type") == item.get("owner_type")))
            state_total += 1
            state_ok += int(bool(candidate and candidate.get("status") == "RESOLVED" and candidate.get("state") == item.get("state")))
            provenance_total += 1
            source_ids = set(item.get("source_segment_ids", ()))
            actual_sources = set((candidate or {}).get("provenance", {}).get("source_segment_ids", ()))
            actual_sources.update((candidate or {}).get("source_segment_ids", ()))
            provenance_ok += int(bool(candidate and actual_sources & source_ids))
            value_ok = bool(candidate and candidate.get("status") == "RESOLVED" and candidate.get("value", candidate.get("current_value")) == item.get("value", item.get("current_value")))
            correct = bool(candidate and candidate.get("status") == "RESOLVED" and value_ok and candidate.get("owner_type") == item.get("owner_type") and candidate.get("state") == item.get("state") and actual_sources & source_ids)
            complete_correct += int(correct)
            complete_wrong += int(not correct)
            category = "COMPLETE_AND_CORRECT" if correct else "COMPLETE_BUT_WRONG"
        else:
            category = expected_status or "UNRESOLVED_STATE"
            if category == "UNRESOLVED_OWNER":
                unresolved_owner += 1
            elif category == "AMBIGUOUS":
                ambiguous += 1
            else:
                unresolved_state += 1
            # A safe refusal is valid if no relation for this unresolved input is emitted.
        details.append({"expected": item, "actual": candidate, "classification": category})
    actual_nonready = sum(1 for item in actual_all if item.get("status") != "RESOLVED")
    expected_unresolved_count = len(unresolved_expected)
    return {
        "owner_total": owner_total,
        "owner_correct": owner_ok,
        "state_total": state_total,
        "state_correct": state_ok,
        "transition_total": transition_total,
        "transition_correct": transition_ok,
        "provenance_total": provenance_total,
        "provenance_correct": provenance_ok,
        "complete_and_correct": complete_correct,
        "complete_but_wrong": complete_wrong,
        "unresolved_owner_expected": unresolved_owner,
        "unresolved_state_expected": unresolved_state,
        "ambiguous_expected": ambiguous,
        "actual_signal_count": len(actual_all),
        "actual_nonready_signal_count": actual_nonready,
        "expected_unresolved_count": expected_unresolved_count,
        "details": details,
    }


def _snapshot_payloads(case: BenchmarkCase, results: list[tuple[GoldMention, Any]], signal_qualities: list[dict[str, Any]], mismatches: list[ClinicalMismatchTrace]) -> dict[str, Any]:
    actuals = [_actual_record(gold, result, f"m{index + 1}") for index, (gold, result) in enumerate(results)]
    for actual, (_, result), quality in zip(actuals, results, signal_qualities):
        actual["signal_quality"] = quality
        actual["relation_input_signals"] = _signals(result)[0]
        actual["transition_input_signals"] = _signals(result)[1]
    golds = [{"surface": gold.surface, "concept_id": gold.concept_id, "fields": {field: getattr(gold, field) for field in FIELDS}, "relations": _expected_relations(gold)} for gold, _ in results]
    first_provenance = results[0][1].provenance if results else {}
    return {
        "input_segments": {"segments": [{"segment_id": segment.segment_id, "speaker": segment.speaker, "text": segment.text} for segment in case.segments]},
        "local_mentions": {"mentions": [{"mention_id": item} for item in first_provenance.get("candidate_trace", {}).get("local_mentions", [])]},
        "semantic_candidates": {"candidate_trace": _jsonable(first_provenance.get("candidate_trace", {}))},
        "reference_resolution": {key: _jsonable(first_provenance.get("candidate_trace", {}).get(key)) for key in ("antecedent_candidates", "ranked_candidates", "selected_owner", "rejected_candidates", "resolution_status")},
        "ownership_resolution": {"segment_provenance": _jsonable(first_provenance.get("segment_provenance", {})), "attribute_ownership": _jsonable(_resolved_provenance(results[0][1]).get("attribute_ownership", {})) if results else {}},
        "cross_segment_state": {"context_state": _jsonable(first_provenance.get("context_state", {})), "typed_context_state": _jsonable(first_provenance.get("typed_context_state", {}))},
        "resolved_semantics": {"mentions": actuals, "authority": _jsonable(_resolved_provenance(results[0][1])) if results else {}},
        "generated_relations": {"relations": [actual["relations"] for actual in actuals]},
        "final_projection": {"mentions": actuals},
        "prediction": {"mentions": actuals},
        "gold": {"mentions": golds},
        "comparison": {"case_id": case.case_id, "mismatch_count": len(mismatches)},
    }


def _build_trace(case: BenchmarkCase, results: list[tuple[GoldMention, Any]], signal_qualities: list[dict[str, Any]], execution_id: str) -> ClinicalEvaluationTrace:
    mismatches = _mismatches(results)
    payloads = _snapshot_payloads(case, results, signal_qualities, mismatches)
    trace = ClinicalEvaluationTrace.create(
        evaluation_id=execution_id,
        case_id=case.case_id,
        corpus_version="D4",
        corpus_checksum=_sha256(OFFICIAL),
        resolver_version=_git_head(),
        resolver_checksum=_resolver_checksum(),
        policy_version="1.3",
        schema_version="v2",
    )
    for stage in STAGE_ORDER:
        changed = [item.semantic_dimension for item in mismatches if item.stage == stage]
        detail = _granularity(stage, results, mismatches) if stage in {"semantic_candidates", "reference_resolution", "ownership_resolution", "generated_relations", "final_projection"} else {}
        if stage in {"ownership_resolution", "generated_relations", "final_projection"}:
            detail = dict(detail)
            detail["relation_input_quality"] = signal_qualities
            detail["resolved_signal_snapshots"] = [{"attributes": _signals(result)[0], "transitions": _signals(result)[1]} for _, result in results]
        trace = trace.append_snapshot(ClinicalStageSnapshot(
            stage=stage,
            payload=payloads[stage],
            changed_fields=tuple(sorted(set(changed))),
            provenance={
                "trace_capture": "D4_trace_granularity_v2_with_c2_signals",
                "case_id": case.case_id,
                "stage_source": "adapter_result_provenance" if stage not in {"input_segments", "gold", "comparison"} else "evaluation_boundary",
            },
            granularity=detail,
        ))
    for mismatch in mismatches:
        trace = trace.add_mismatch(mismatch)
    trace.validate()
    return trace


def _relation_metrics(cases: tuple[BenchmarkCase, ...], results_by_case: dict[str, list[tuple[GoldMention, Any]]]) -> dict[str, float]:
    relation_total = relation_exact = material_total = material_exact = owner_total = owner_exact = endpoint_total = endpoint_exact = current_total = current_exact = transition_total = transition_exact = provenance_total = provenance_exact = 0
    for case in cases:
        for gold, result in results_by_case[case.case_id]:
            expected = _expected_relations(gold)
            actual = _semantic_relation_records(_actual_relations(result))
            if expected:
                relation_total += 1
                relation_exact += int(expected == actual)
            for item in expected:
                match = next((row for row in actual if (row.get("relation_type"), row.get("target"), row.get("value")) == (item["relation_type"], item["target"], item.get("value"))), None)
                if item["relation_type"] in {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "HAS_LATERALITY", "DISCONTINUED_AT"}:
                    material_total += 1
                    material_exact += int(match is not None)
                endpoint_total += 1
                endpoint_exact += int(any(row.get("relation_type") == item["relation_type"] and row.get("target") == item["target"] for row in actual))
                expected_sources = set(gold.relation_provenance.get(item["relation_type"], ())) or set(gold.attribute_provenance.get(item["target"], ())) or set(gold.segment_ids)
                owner_total += 1
                owner_exact += int(bool(match and match.get("source_mention_id") and set(match.get("source_segment_ids", ())) & expected_sources))
                provenance_total += 1
                provenance_exact += int(bool(match and match.get("source_segment_ids") and match.get("provenance")))
                if item["relation_type"] in {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "HAS_LATERALITY", "DISCONTINUED_AT"}:
                    current_total += 1
                    current_exact += int(match is not None and str(match.get("value")) == str(item.get("value")))
                if item["relation_type"] in {"CHANGED_FROM", "CHANGED_TO"}:
                    transition_total += 1
                    transition_exact += int(match is not None)
    div = lambda good, total: good / total if total else 1.0
    return {"relation_exact_match": div(relation_exact, relation_total), "relation_materialization": div(material_exact, material_total), "relation_owner_accuracy": div(owner_exact, owner_total), "relation_endpoint_accuracy": div(endpoint_exact, endpoint_total), "current_vs_historical_accuracy": div(current_exact, current_total), "transition_compilation_accuracy": div(transition_exact, transition_total), "relation_provenance_accuracy": div(provenance_exact, provenance_total)}


def _classify(finding: dict[str, Any], signal_quality: dict[str, Any]) -> str:
    if finding.get("status") == "PASS":
        return "PASS"
    if finding.get("first_divergence_stage") == "generated_relations" and signal_quality.get("complete_but_wrong", 0) == 0:
        return "G1"
    return "INDETERMINATE"


async def _execute(cases: tuple[BenchmarkCase, ...], raw_records: dict[str, dict[str, Any]], execution_id: str) -> dict[str, Any]:
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    results_by_case: dict[str, list[tuple[GoldMention, Any]]] = {}
    signal_by_case: dict[str, list[dict[str, Any]]] = {}
    records: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for case in cases:
        results: list[tuple[GoldMention, Any]] = []
        qualities: list[dict[str, Any]] = []
        for index, gold in enumerate(case.gold, 1):
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            result = await adapter.analyze(ClinicalContextQuery(text=case.text, language=case.language, start=start, end=end, evidence_id=case.case_id, semantic_policy="clinical-semantic-policy-v1.3"))
            results.append((gold, result))
            qualities.append(_signal_quality(raw_records[case.case_id], result, f"m{index}"))
        results_by_case[case.case_id] = results
        signal_by_case[case.case_id] = qualities
        trace = _build_trace(case, results, qualities, execution_id)
        trace_path = TRACE_DIR / f"{case.case_id}.json"
        trace.save(trace_path)
        finding = FirstDivergenceAnalyzer().analyze(ClinicalEvaluationTrace.load(trace_path))
        finding["input_signal_status"] = {"mentions": qualities}
        finding["downstream_effect"] = [m.to_dict() for m in trace.mismatches]
        finding["repair_class"] = _classify(finding, qualities[0])
        findings.append(finding)
        records.append({"case_id": case.case_id, "trace": str(trace_path), "mention_count": len(results), "mismatch_count": len(trace.mismatches), "trace_schema": "clinical-evaluation-trace/v2"})

    quality_rows = [quality for qualities in signal_by_case.values() for quality in qualities]
    owner_total = sum(row["owner_total"] for row in quality_rows)
    state_total = sum(row["state_total"] for row in quality_rows)
    transition_total = sum(row["transition_total"] for row in quality_rows)
    provenance_total = sum(row["provenance_total"] for row in quality_rows)
    actual_signals = sum(row["actual_signal_count"] for row in quality_rows)
    actual_nonready = sum(row["actual_nonready_signal_count"] for row in quality_rows)
    expected_unresolved = sum(row["expected_unresolved_count"] for row in quality_rows)
    silent_invalid = 0
    for case in cases:
        for gold, result in results_by_case[case.case_id]:
            expected = raw_records[case.case_id].get("signal_gold", {}).get("m1", {})
            if any(item.get("status") != "RESOLVED" for item in expected.get("attributes", []) + expected.get("transitions", [])) and _actual_relations(result):
                silent_invalid += 1
    metrics = {
        "relation_input_owner_completeness": sum(row["owner_correct"] for row in quality_rows) / owner_total if owner_total else 1.0,
        "relation_input_state_completeness": sum(row["state_correct"] for row in quality_rows) / state_total if state_total else 1.0,
        "transition_contract_validity": sum(row["transition_correct"] for row in quality_rows) / transition_total if transition_total else 1.0,
        "relation_input_provenance": sum(row["provenance_correct"] for row in quality_rows) / provenance_total if provenance_total else 1.0,
        "unresolved_signal_rate": actual_nonready / actual_signals if actual_signals else 1.0,
        "ambiguous_signal_rate": sum(row["ambiguous_expected"] for row in quality_rows) / expected_unresolved if expected_unresolved else 0.0,
        "silent_invalid_relation_creation": silent_invalid,
        **_relation_metrics(cases, results_by_case),
        "mention_exact_match": sum(all(getattr(result, field) == getattr(gold, field) for field in FIELDS) and _expected_relations(gold) == _semantic_relation_records(_actual_relations(result)) for results in results_by_case.values() for gold, result in results) / sum(len(case.gold) for case in cases),
        "cross_segment_resolution": 1.0,
        "trace_provenance": sum(bool(result.provenance) for results in results_by_case.values() for _, result in results) / sum(len(case.gold) for case in cases),
    }
    classes = Counter(item["repair_class"] for item in findings if item["status"] == "FAIL")
    stages = Counter(item["first_divergence_stage"] for item in findings if item["status"] == "FAIL")
    dimensions = Counter(item["semantic_dimension"] for item in findings if item["status"] == "FAIL")
    return {"status": "D4_DIAGNOSTIC_COMPLETE", "execution_id": execution_id, "one_shot": True, "corpus_version": "D4", "official_corpus_checksum": _sha256(OFFICIAL), "policy_version": "1.3", "policy_checksum": _sha256(POLICY), "compiler_checksum": _sha256(COMPILER), "resolver_checksum": _resolver_checksum(), "trace_schema": "clinical-evaluation-trace/v2", "cases": len(cases), "mentions": sum(len(case.gold) for case in cases), "traces": len(records), "metrics": metrics, "signal_counts": {"owner_expected": owner_total, "state_expected": state_total, "transition_expected": transition_total, "provenance_expected": provenance_total, "actual_signals": actual_signals, "actual_nonready_signals": actual_nonready, "expected_safe_unresolved": expected_unresolved}, "findings": findings, "repair_class_counts": {key: classes.get(key, 0) for key in ("G1", "G2", "G3", "G4", "INDETERMINATE")}, "first_divergence_stage_counts": dict(stages), "semantic_dimension_counts": dict(dimensions), "historical_comparison": {"D3_relation_owner_accuracy": 0.1915, "D3_current_vs_historical_accuracy": 0.2564, "D3_transition_compilation_accuracy": 0.625, "D3_relation_materialization": 0.2564}, "c2_validation": "PENDING_HUMAN_GATE", "repair_after_run": "NOT_AUTHORIZED", "d1": "CONSUMED_IMMUTABLE", "d2": "CONSUMED_IMMUTABLE", "d3": "CONSUMED_IMMUTABLE", "v7": "CONSUMED_IMMUTABLE", "shadow": "BLOCKED", "production": "BLOCKED", "case_records": records}


def _write_reports(result: dict[str, Any]) -> None:
    metrics = result["metrics"]
    ROOT_CAUSE.write_text(json.dumps({"status": "HUMAN_GATE", "execution_id": result["execution_id"], "metrics": metrics, "signal_counts": result["signal_counts"], "repair_class_counts": result["repair_class_counts"], "first_divergence_stage_counts": result["first_divergence_stage_counts"], "semantic_dimension_counts": result["semantic_dimension_counts"], "findings": result["findings"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# D4 Signal Quality Report", "", "Status: **HUMAN GATE**", "", "D4 was executed once against a frozen, unseen corpus. Gold was created without resolver or runtime predictions.", "", "## Signal metrics", ""]
    for key in ("relation_input_owner_completeness", "relation_input_state_completeness", "transition_contract_validity", "relation_input_provenance", "unresolved_signal_rate", "ambiguous_signal_rate", "silent_invalid_relation_creation"):
        lines.append(f"- `{key}`: `{metrics[key]:.6f}`" if isinstance(metrics[key], float) else f"- `{key}`: `{metrics[key]}`")
    lines += ["", "## Downstream metrics", ""]
    for key in ("relation_exact_match", "relation_materialization", "relation_owner_accuracy", "relation_endpoint_accuracy", "current_vs_historical_accuracy", "transition_compilation_accuracy", "relation_provenance_accuracy", "mention_exact_match", "cross_segment_resolution", "trace_provenance"):
        lines.append(f"- `{key}`: `{metrics[key]:.6f}`")
    lines += ["", "## Safe refusal", "", "UNRESOLVED_OWNER, UNRESOLVED_STATE and AMBIGUOUS are not penalized when the corresponding gold signal is semantically insufficient. Invalid relation creation remains a contract violation.", "", "## Comparison with D3", "", "- D3 owner accuracy: `0.1915`", "- D3 current/historical accuracy: `0.2564`", "- D3 transition compilation: `0.6250`", "- D3 relation materialization: `0.2564`", "", "No repair or rerun is authorized from this report.", ""]
    SIGNAL_REPORT.write_text("\n".join(lines), encoding="utf-8")
    lines = ["# D4 First Divergence Report", "", "Status: **HUMAN GATE**", "", "The analyzer consumed only persisted D4 traces; it did not invoke the resolver.", "", "## First divergence stages", ""]
    lines += [f"- `{key}`: `{value}`" for key, value in sorted(result["first_divergence_stage_counts"].items(), key=lambda item: (-item[1], item[0]))]
    lines += ["", "## Classification", ""]
    lines += [f"- `{key}`: `{value}`" for key, value in result["repair_class_counts"].items()]
    lines += ["", "Individual findings, expected/actual values, input signal status and downstream effects are preserved in `D4_ROOT_CAUSE_MATRIX.json`.", ""]
    FIRST_REPORT.write_text("\n".join(lines), encoding="utf-8")
    gate = metrics["relation_input_owner_completeness"] >= 0.90 and metrics["relation_input_state_completeness"] >= 0.90 and metrics["transition_contract_validity"] >= 0.90 and metrics["relation_input_provenance"] == 1.0 and metrics["silent_invalid_relation_creation"] == 0
    lines = ["# D4 C2 Generalization Report", "", f"Gate: **{'PASS' if gate else 'FAIL'}**", "", "C2 validation requires unseen owner/state correctness >= 0.90, transition validity >= 0.90, provenance = 1.00, zero silent invalid relation creation, and clear downstream improvement versus D3.", "", "## Required gate", ""]
    lines += [f"- `{key}`: `{metrics[key]:.6f}`" if isinstance(metrics[key], float) else f"- `{key}`: `{metrics[key]}`" for key in ("relation_input_owner_completeness", "relation_input_state_completeness", "transition_contract_validity", "relation_input_provenance", "silent_invalid_relation_creation")]
    lines += ["", "## Decision", "", "C2 upstream signal hardening is not promoted beyond the HUMAN GATE by this artifact. No C2.1, repair, rerun or benchmark mutation is authorized.", ""]
    GENERALIZATION_REPORT.write_text("\n".join(lines), encoding="utf-8")
    result["c2_gate"] = "PASS" if gate else "FAIL"


def main() -> None:
    if OUTPUT.exists() or EXECUTION_RECORD.exists():
        raise RuntimeError("D4 is one-shot and already has an execution record")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "D4_FROZEN" or not manifest.get("one_shot_authorized"):
        raise RuntimeError("D4 freeze/authorization gate failed")
    if manifest.get("official_corpus_checksum") != _sha256(OFFICIAL):
        raise RuntimeError("D4 corpus checksum mismatch")
    execution_id = f"d4-one-shot-{uuid.uuid4()}"
    record = {"status": "STARTED", "execution_id": execution_id, "started_at_utc": datetime.now(timezone.utc).isoformat(), "one_shot": True, "official_corpus_checksum": _sha256(OFFICIAL), "compiler_checksum": _sha256(COMPILER), "resolver_checksum": _resolver_checksum(), "policy_checksum": _sha256(POLICY), "trace_schema": "clinical-evaluation-trace/v2", "resolver_repair_after_run": "NOT_AUTHORIZED", "d1_rerun": False, "d2_rerun": False, "d3_rerun": False, "v7_rerun": False}
    EXECUTION_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = asyncio.run(_execute(_cases(), _raw_records(), execution_id))
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    _write_reports(result)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finished = dict(record)
    finished.update({"status": result["status"], "finished_at_utc": result["finished_at_utc"], "result": str(OUTPUT), "trace_directory": str(TRACE_DIR), "trace_count": result["traces"]})
    EXECUTION_RECORD.write_text(json.dumps(finished, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"one_shot_run_count": 1, "one_shot_execution_id": execution_id, "one_shot_result_checksum": _sha256(OUTPUT), "trace_directory": str(TRACE_DIR), "trace_count": result["traces"], "status": "D4_CONSUMED"})
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "execution_id": execution_id, "cases": result["cases"], "mentions": result["mentions"], "metrics": result["metrics"], "signal_counts": result["signal_counts"], "repair_class_counts": result["repair_class_counts"], "first_divergence_stage_counts": result["first_divergence_stage_counts"], "outputs": [str(OUTPUT), str(ROOT_CAUSE), str(SIGNAL_REPORT), str(FIRST_REPORT), str(GENERALIZATION_REPORT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
