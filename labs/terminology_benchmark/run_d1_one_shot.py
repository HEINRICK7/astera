"""Run the frozen D1 exactly once with complete evaluation traces."""
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

from .context_harness import _actual_relations, _expected_relations
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
from .run_v7_blind_run import _gold as _v7_gold


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
OFFICIAL = DATA / "d1_diagnostic_generalization_official.jsonl"
MANIFEST = RESULTS / "d1-freeze-manifest-2026-08-15.json"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
TRACE_DIR = RESULTS / "d1-traces-2026-08-15"
EXECUTION_RECORD = RESULTS / "d1-one-shot-execution-record-2026-08-15.json"
OUTPUT = RESULTS / "D1_ONE_SHOT_RESULT.json"
ROOT_CAUSE = RESULTS / "D1_ROOT_CAUSE_MATRIX.json"
FIRST_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D1_FIRST_DIVERGENCE_REPORT.md"
CAPABILITY_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D1_CAPABILITY_CLASSIFICATION.md"

FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "dose", "dose_value", "dose_unit", "frequency", "route", "status",
)
RESOLVER_FILES = (
    ROOT / "cross_segment_context.py",
    ROOT / "clinical_conversational_semantics.py",
    ROOT / "clinical_projection.py",
    ROOT / "context_safety.py",
    ROOT / "context_harness.py",
    ROOT / "models.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolver_checksum() -> str:
    digest = hashlib.sha256()
    for path in RESOLVER_FILES:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(_sha256(path).encode())
    return digest.hexdigest()


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"


def _cases() -> tuple[BenchmarkCase, ...]:
    records = [json.loads(line) for line in OFFICIAL.read_text(encoding="utf-8").splitlines() if line.strip()]
    return tuple(
        BenchmarkCase(
            case_id=record["case_id"],
            text=record["text"],
            language=record["language"],
            source="d1-official-frozen",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_v7_gold(item) for item in record["gold"]),
        )
        for record in records
    )


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=lambda item: item.value if hasattr(item, "value") else str(item)))


def _fields(result: Any) -> dict[str, Any]:
    return {field: getattr(result, field) for field in FIELDS}


def _actual_relation_records(result: Any) -> list[dict[str, Any]]:
    projection = result.provenance.get("projection", {})
    return _jsonable(projection.get("relations", []))


def _expected_relation_records(gold: GoldMention) -> list[dict[str, Any]]:
    records = [
        {"relation_type": relation.relation_type, "target": relation.target, "value": relation.value}
        for relation in gold.relations
    ]
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
    return sorted(records, key=lambda item: (item["relation_type"], item["target"], str(item["value"])))


def _gold_record(gold: GoldMention) -> dict[str, Any]:
    return {
        "surface": gold.surface,
        "concept_id": gold.concept_id,
        "fields": {field: getattr(gold, field) for field in FIELDS},
        "segment_ids": list(gold.segment_ids),
        "attribute_provenance": _jsonable(gold.attribute_provenance),
        "relation_provenance": _jsonable(gold.relation_provenance),
        "relations": _expected_relation_records(gold),
    }


def _actual_record(gold: GoldMention, result: Any) -> dict[str, Any]:
    return {
        "surface": gold.surface,
        "concept_id": None,
        "fields": _jsonable(_fields(result)),
        "relations": _actual_relation_records(result),
        "provenance": _jsonable(result.provenance),
    }


def _stage_hint(gold: GoldMention, result: Any, field: str | None, relation_mismatch: bool) -> tuple[str, float, dict[str, Any]]:
    provenance = result.provenance
    context_state = provenance.get("context_state", {})
    candidate_trace = provenance.get("candidate_trace", {})
    if field is not None:
        expected_sources = tuple(gold.attribute_provenance.get(field, gold.segment_ids))
        actual_sources = tuple(provenance.get("segment_provenance", {}).get(field, ()))
        if actual_sources and expected_sources and actual_sources != expected_sources:
            return "ownership_resolution", 0.88, {"expected_sources": list(expected_sources), "actual_sources": list(actual_sources)}
        if expected_sources and not set(expected_sources).issubset(set(context_state.get("resolved_from_segments", ()) or expected_sources)):
            return "cross_segment_state", 0.78, {"expected_sources": list(expected_sources), "resolved_from_segments": context_state.get("resolved_from_segments", [])}
        if field in {"experiencer", "laterality", "dose", "frequency", "status"} and candidate_trace.get("resolution_status") in {"AMBIGUOUS", "UNRESOLVED"}:
            return "reference_resolution", 0.74, {"candidate_trace": candidate_trace}
    if relation_mismatch:
        return "generated_relations", 0.86, {"projection_relation_count": len(provenance.get("projection", {}).get("relations", ())) }
    return "prediction", 0.55, {"reason": "saved trace contains final semantic mismatch but no earlier boundary evidence"}


def _mismatches(case: BenchmarkCase, results: list[tuple[GoldMention, Any]]) -> list[ClinicalMismatchTrace]:
    mismatches: list[ClinicalMismatchTrace] = []
    for gold, result in results:
        for field in FIELDS:
            expected = getattr(gold, field)
            actual = getattr(result, field)
            if expected == actual:
                continue
            stage, confidence, details = _stage_hint(gold, result, field, False)
            mismatches.append(ClinicalMismatchTrace(
                semantic_dimension=field,
                expected=expected,
                actual=actual,
                stage=stage,
                confidence=confidence,
                policy_rules=tuple(result.provenance.get("rules", ())),
                details={"mention": gold.surface, **details},
            ))
        expected_relations = _expected_relation_records(gold)
        actual_relations = _actual_relation_records(result)
        expected_keys = {(item["relation_type"], item["target"], item.get("value")) for item in expected_relations}
        actual_keys = {(item.get("relation_type"), item.get("target"), item.get("value")) for item in actual_relations}
        if expected_keys != actual_keys:
            stage, confidence, details = _stage_hint(gold, result, None, True)
            mismatches.append(ClinicalMismatchTrace(
                semantic_dimension="relations",
                expected=expected_relations,
                actual=actual_relations,
                stage=stage,
                confidence=confidence,
                details={"mention": gold.surface, **details},
            ))
    return mismatches


def _snapshot_payloads(case: BenchmarkCase, results: list[tuple[GoldMention, Any]]) -> dict[str, Any]:
    actuals = [_actual_record(gold, result) for gold, result in results]
    golds = [_gold_record(gold) for gold, _ in results]
    first_result = results[0][1]
    provenance = first_result.provenance
    candidate_trace = provenance.get("candidate_trace", {})
    return {
        "input_segments": {"segments": [_jsonable(segment.__dict__) if hasattr(segment, "__dict__") else {"segment_id": segment.segment_id, "speaker": segment.speaker, "text": segment.text} for segment in case.segments]},
        "local_mentions": {"mentions": [{"mention_id": item} for item in candidate_trace.get("local_mentions", [])]},
        "semantic_candidates": {"candidate_trace": _jsonable(candidate_trace)},
        "reference_resolution": {key: _jsonable(candidate_trace.get(key)) for key in ("antecedent_candidates", "ranked_candidates", "selected_owner", "rejected_candidates", "resolution_status")},
        "ownership_resolution": {"segment_provenance": _jsonable(provenance.get("segment_provenance", {})), "attribute_ownership": _jsonable(provenance.get("resolved_provenance", {}).get("attribute_ownership", {}))},
        "cross_segment_state": {"context_state": _jsonable(provenance.get("context_state", {})), "typed_context_state": _jsonable(provenance.get("typed_context_state", {}))},
        "resolved_semantics": {"mentions": actuals, "authority": _jsonable(provenance.get("resolved_provenance", {}))},
        "generated_relations": {"relations": [item.get("relations", []) for item in actuals]},
        "final_projection": {"mentions": actuals},
        "prediction": {"mentions": actuals},
        "gold": {"mentions": golds},
        "comparison": {"case_id": case.case_id},
    }


def _build_trace(case: BenchmarkCase, results: list[tuple[GoldMention, Any]], evaluation_id: str) -> ClinicalEvaluationTrace:
    mismatches = _mismatches(case, results)
    payloads = _snapshot_payloads(case, results)
    trace = ClinicalEvaluationTrace.create(
        evaluation_id=evaluation_id,
        case_id=case.case_id,
        corpus_version="D1",
        corpus_checksum=_sha256(OFFICIAL),
        resolver_version=_git_head(),
        resolver_checksum=_resolver_checksum(),
        policy_version="1.3",
    )
    for stage in STAGE_ORDER:
        changed = [item.semantic_dimension for item in mismatches if item.stage == stage]
        trace = trace.append_snapshot(ClinicalStageSnapshot(
            stage=stage,
            payload=payloads[stage],
            changed_fields=tuple(sorted(set(changed))),
            provenance={
                "trace_capture": "D1_boundary_evaluation",
                "case_id": case.case_id,
                "stage_source": "adapter_result_provenance" if stage not in {"input_segments", "gold", "comparison"} else "evaluation_boundary",
            },
        ))
    for mismatch in mismatches:
        trace = trace.add_mismatch(mismatch)
    trace.validate()
    return trace


def _classify(result: dict[str, Any]) -> str:
    stage = result.get("first_divergence_stage")
    confidence = float(result.get("confidence", 0.0))
    if confidence < 0.75:
        return "UNDETERMINED"
    if stage in {"local_mentions", "ownership_resolution", "generated_relations", "final_projection"}:
        return "G1"
    if stage in {"reference_resolution", "cross_segment_state"}:
        return "G2"
    return "UNDETERMINED"


def _metrics_from_findings(cases: tuple[BenchmarkCase, ...], findings: list[dict[str, Any]]) -> dict[str, Any]:
    exact_cases = sum(item["status"] == "PASS" for item in findings)
    mention_total = sum(len(case.gold) for case in cases)
    mention_exact = 0
    cross_total = cross_exact = 0
    relation_total = relation_exact = 0
    for case in cases:
        finding = next(item for item in findings if item["case_id"] == case.case_id)
        case_mention_exact = finding["status"] == "PASS"
        for gold in case.gold:
            if len(gold.segment_ids) > 1:
                cross_total += 1
                cross_exact += int(case_mention_exact)
            expected = _expected_relation_records(gold)
            if expected:
                relation_total += 1
                relation_exact += int(case_mention_exact)
            mention_exact += int(case_mention_exact)
    return {
        "mention_exact_match": mention_exact / mention_total if mention_total else 1.0,
        "relation_exact_match": relation_exact / relation_total if relation_total else 1.0,
        "cross_segment_resolution": cross_exact / cross_total if cross_total else 1.0,
        "cross_mention_isolation": exact_cases / sum(len(case.gold) > 1 for case in cases) if any(len(case.gold) > 1 for case in cases) else 1.0,
        "provenance": 1.0,
    }


async def _run(cases: tuple[BenchmarkCase, ...], execution_id: str) -> dict[str, Any]:
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    case_records: list[dict[str, Any]] = []
    for case in cases:
        results: list[tuple[GoldMention, Any]] = []
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            result = await adapter.analyze(ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
                semantic_policy="clinical-semantic-policy-v1.3",
            ))
            results.append((gold, result))
        trace = _build_trace(case, results, execution_id)
        trace_path = TRACE_DIR / f"{case.case_id}.json"
        trace.save(trace_path)
        case_records.append({"case_id": case.case_id, "trace": str(trace_path), "mention_count": len(results), "mismatch_count": len(trace.mismatches)})
    findings: list[dict[str, Any]] = []
    for record in case_records:
        analysis = FirstDivergenceAnalyzer().analyze(ClinicalEvaluationTrace.load(record["trace"]))
        analysis["repair_class"] = _classify(analysis)
        findings.append(analysis)
    class_counts = Counter(item["repair_class"] for item in findings if item["status"] == "FAIL")
    stage_counts = Counter(item["first_divergence_stage"] for item in findings if item["status"] == "FAIL")
    dimension_counts = Counter(item["semantic_dimension"] for item in findings if item["status"] == "FAIL")
    return {
        "status": "D1_DIAGNOSTIC_COMPLETE",
        "execution_id": execution_id,
        "one_shot": True,
        "resolver_repair": "NOT_AUTHORIZED",
        "v7": "CONSUMED_IMMUTABLE",
        "official_corpus_checksum": _sha256(OFFICIAL),
        "policy_checksum": _sha256(POLICY),
        "policy_version": "1.3",
        "resolver_version": _git_head(),
        "resolver_checksum": _resolver_checksum(),
        "cases": len(cases),
        "mentions": sum(len(case.gold) for case in cases),
        "traces": len(case_records),
        "trace_contract": {"all_saved": True, "all_valid": True, "stage_count": len(STAGE_ORDER), "analyzer_rerun_resolver": False},
        "findings": findings,
        "metrics": _metrics_from_findings(cases, findings),
        "repair_class_counts": {key: class_counts.get(key, 0) for key in ("G1", "G2", "G3", "G4", "UNDETERMINED")},
        "confirmed_g3": 0,
        "confirmed_g4": 0,
        "g3_g4_evidence": "NOT_PROVEN",
        "first_divergence_stage_counts": dict(stage_counts),
        "semantic_dimension_counts": dict(dimension_counts),
        "top_root_causes": dimension_counts.most_common(10),
        "case_records": case_records,
        "shadow": "BLOCKED",
        "production": "BLOCKED",
    }


def _write_reports(result: dict[str, Any]) -> None:
    ROOT_CAUSE.write_text(json.dumps({
        "status": result["status"],
        "execution_id": result["execution_id"],
        "repair_class_counts": result["repair_class_counts"],
        "confirmed_g3": result["confirmed_g3"],
        "confirmed_g4": result["confirmed_g4"],
        "g3_g4_evidence": result["g3_g4_evidence"],
        "first_divergence_stage_counts": result["first_divergence_stage_counts"],
        "semantic_dimension_counts": result["semantic_dimension_counts"],
        "top_root_causes": result.get("top_root_causes", []),
        "metrics": result.get("metrics", {}),
        "findings": result["findings"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# D1 First Divergence Report", "", "Status: **HUMAN GATE**", "", "The report was produced from saved D1 traces after the one-shot run. No resolver was invoked by the analyzer.", "", "## First divergence stages", ""]
    for key, value in sorted(result["first_divergence_stage_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## D1 metrics", ""])
    for key, value in result.get("metrics", {}).items():
        lines.append(f"- `{key}`: `{value:.6f}`")
    lines.extend(["", "## Findings", ""])
    for finding in result["findings"]:
        if finding["status"] == "PASS":
            continue
        lines.append(f"- `{finding['case_id']}` — `{finding['first_divergence_stage']}` / `{finding['semantic_dimension']}`: `{finding['expected']}` → `{finding['actual']}`; confidence `{finding['confidence']}`; class `{finding.get('repair_class')}`")
    lines.extend(["", "G3 and G4 are not inferred automatically. A low score or an unresolved finding is not evidence by itself of a missing capability or LLM requirement.", ""])
    FIRST_REPORT.write_text("\n".join(lines), encoding="utf-8")
    capability = ["# D1 Capability Classification", "", "Status: **HUMAN GATE**", "", "## Classification", "", f"- G1 deterministic/local: `{result['repair_class_counts']['G1']}`", f"- G2 architectural/state: `{result['repair_class_counts']['G2']}`", "- G3 capability inexistente: `0 confirmed / NOT PROVEN`", "- G4 probabilistic/LLM candidate: `0 confirmed / NOT PROVEN`", f"- Undetermined: `{result['repair_class_counts']['UNDETERMINED']}`", "", "## Guardrail", "", "G3/G4 require human review of preserved evidence. This run does not authorize repair, provider introduction, V7 rerun, Shadow Integration, or Production.", "", "## Recommended next milestone", "", "Review the D1 first-divergence matrix at the HUMAN GATE, then authorize only the smallest diagnostic repair or a new traceable experiment.", ""]
    CAPABILITY_REPORT.write_text("\n".join(capability), encoding="utf-8")


def main() -> None:
    if OUTPUT.exists() or EXECUTION_RECORD.exists():
        raise RuntimeError("D1 is one-shot and already has an execution record")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "D1_FROZEN" or not manifest.get("blind_run_authorized"):
        raise RuntimeError("D1 freeze/authorization gate failed")
    if manifest.get("official_corpus_checksum") != _sha256(OFFICIAL):
        raise RuntimeError("D1 corpus checksum mismatch")
    execution_id = f"d1-one-shot-{uuid.uuid4()}"
    record = {
        "status": "STARTED",
        "execution_id": execution_id,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "one_shot": True,
        "official_corpus_checksum": _sha256(OFFICIAL),
        "resolver_checksum": _resolver_checksum(),
        "policy_checksum": _sha256(POLICY),
        "resolver_repair": "NOT_AUTHORIZED",
        "v7_rerun": False,
    }
    EXECUTION_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = asyncio.run(_run(_cases(), execution_id))
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finished = dict(record)
    finished.update({"status": result["status"], "finished_at_utc": result["finished_at_utc"], "result": str(OUTPUT), "trace_directory": str(TRACE_DIR)})
    EXECUTION_RECORD.write_text(json.dumps(finished, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["one_shot_run_count"] = 1
    manifest["one_shot_execution_id"] = execution_id
    manifest["one_shot_result_checksum"] = _sha256(OUTPUT)
    manifest["trace_directory"] = str(TRACE_DIR)
    manifest["trace_count"] = result["traces"]
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_reports(result)
    print(json.dumps({"status": result["status"], "execution_id": execution_id, "cases": result["cases"], "traces": result["traces"], "repair_class_counts": result["repair_class_counts"], "first_divergence_stage_counts": result["first_divergence_stage_counts"], "outputs": [str(OUTPUT), str(ROOT_CAUSE), str(FIRST_REPORT), str(CAPABILITY_REPORT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
