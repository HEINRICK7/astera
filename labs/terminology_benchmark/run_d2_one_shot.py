"""Execute the frozen D2 once with Trace Granularity v2 enabled."""
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
    TRACE_GRANULARITY_V2_FIELDS,
)
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
OFFICIAL = DATA / "d2_diagnostic_generalization_official.jsonl"
MANIFEST = RESULTS / "D2_FREEZE_MANIFEST.json"
EXECUTION_RECORD = RESULTS / "d2-one-shot-execution-record-2026-08-15.json"
TRACE_DIR = RESULTS / "d2-traces-2026-08-15"
OUTPUT = RESULTS / "D2_ONE_SHOT_RESULT.json"
ROOT_CAUSE = RESULTS / "D2_ROOT_CAUSE_MATRIX.json"
FIRST_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D2_FIRST_DIVERGENCE_REPORT.md"
CAPABILITY_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D2_CAPABILITY_CLASSIFICATION.md"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
D1_RESULT = RESULTS / "D1_ONE_SHOT_RESULT.json"

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


def _gold(item: dict[str, Any]) -> GoldMention:
    return GoldMention(
        **{
            **{key: value for key, value in item.items() if key not in {"relations", "segment_ids", "attribute_provenance", "relation_provenance"}},
            "relations": tuple(
                GoldRelation(relation_type=relation["relation_type"], target=relation["target"], value=relation.get("value"))
                for relation in item.get("relations", ())
            ),
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
            source="d2-official-frozen",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        )
        for record in records
    )


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=lambda item: item.value if hasattr(item, "value") else str(item)))


def _fields(result: Any) -> dict[str, Any]:
    return {field: getattr(result, field) for field in FIELDS}


def _actual_relation_records(result: Any) -> list[dict[str, Any]]:
    return _jsonable(result.provenance.get("projection", {}).get("relations", []))


def _semantic_relation_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [{"relation_type": item.get("relation_type"), "target": item.get("target"), "value": item.get("value")} for item in records],
        key=lambda item: (str(item["relation_type"]), str(item["target"]), str(item.get("value"))),
    )


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
    return _semantic_relation_records(records)


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


def _actual_record(gold: GoldMention, result: Any, mention_key: str) -> dict[str, Any]:
    return {
        "mention_id": mention_key,
        "surface": gold.surface,
        "concept_id": None,
        "fields": _jsonable(_fields(result)),
        "relations": _semantic_relation_records(_actual_relation_records(result)),
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
        resolved_from = context_state.get("resolved_from_segments", ()) or expected_sources
        if expected_sources and not set(expected_sources).issubset(set(resolved_from)):
            return "cross_segment_state", 0.78, {"expected_sources": list(expected_sources), "resolved_from_segments": list(resolved_from)}
        if field in {"experiencer", "laterality", "dose", "frequency", "status"} and candidate_trace.get("resolution_status") in {"AMBIGUOUS", "UNRESOLVED"}:
            return "reference_resolution", 0.74, {"candidate_trace": candidate_trace}
    if relation_mismatch:
        return "generated_relations", 0.86, {"relation_output_count": len(provenance.get("projection", {}).get("relations", ())) }
    return "prediction", 0.55, {"reason": "saved v2 trace contains semantic mismatch without earlier boundary evidence"}


def _mismatches(results: list[tuple[GoldMention, Any]]) -> list[ClinicalMismatchTrace]:
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
        expected = _expected_relation_records(gold)
        actual = _semantic_relation_records(_actual_relation_records(result))
        if expected != actual:
            stage, confidence, details = _stage_hint(gold, result, None, True)
            mismatches.append(ClinicalMismatchTrace(
                semantic_dimension="relations",
                expected=expected,
                actual=actual,
                stage=stage,
                confidence=confidence,
                details={"mention": gold.surface, **details},
            ))
    return mismatches


def _per_mention(results: list[tuple[GoldMention, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    attributes: dict[str, Any] = {}
    relations: dict[str, Any] = {}
    for index, (gold, result) in enumerate(results):
        key = f"m{index + 1}"
        attributes[key] = {"surface": gold.surface, "fields": _jsonable(_fields(result))}
        relations[key] = _semantic_relation_records(_actual_relation_records(result))
    return attributes, relations


def _granularity(stage: str, results: list[tuple[GoldMention, Any]], mismatches: list[ClinicalMismatchTrace]) -> dict[str, Any]:
    attributes, relations = _per_mention(results)
    first = results[0][1].provenance if results else {}
    candidate_trace = _jsonable(first.get("candidate_trace", {}))
    resolved = _jsonable(first.get("resolved_provenance", {}))
    segment_provenance = _jsonable(first.get("segment_provenance", {}))
    changed = sorted({item.semantic_dimension for item in mismatches if item.stage == stage})
    dropped = {stage: changed} if changed else {}
    transformed = {stage: changed} if changed else {}
    data: dict[str, Any] = {
        "per_mention_attributes": attributes,
        "per_mention_relations": relations,
        "candidate_to_resolved_field_map": {
            "candidate_trace": candidate_trace,
            "resolved_fields": {key: value["fields"] for key, value in attributes.items()},
        },
        "ownership_decisions": {
            "segment_provenance": segment_provenance,
            "attribute_ownership": resolved.get("attribute_ownership", {}),
        },
        "relation_generation_inputs": {
            "resolved_semantics": {key: value["fields"] for key, value in attributes.items()},
            "existing_projection_relations": _jsonable(first.get("projection", {}).get("relations", [])),
        },
        "relation_generation_outputs": {"relations": relations},
        "projection_field_map": {key: value["fields"] for key, value in attributes.items()},
        "dropped_fields_by_stage": dropped,
        "transformed_fields_by_stage": transformed,
    }
    return data


def _snapshot_payloads(case: BenchmarkCase, results: list[tuple[GoldMention, Any]], mismatches: list[ClinicalMismatchTrace]) -> dict[str, Any]:
    actuals = [_actual_record(gold, result, f"m{index + 1}") for index, (gold, result) in enumerate(results)]
    golds = [_gold_record(gold) for gold, _ in results]
    first_provenance = results[0][1].provenance
    candidate_trace = first_provenance.get("candidate_trace", {})
    return {
        "input_segments": {"segments": [{"segment_id": segment.segment_id, "speaker": segment.speaker, "text": segment.text} for segment in case.segments]},
        "local_mentions": {"mentions": [{"mention_id": item} for item in candidate_trace.get("local_mentions", [])]},
        "semantic_candidates": {"candidate_trace": _jsonable(candidate_trace)},
        "reference_resolution": {key: _jsonable(candidate_trace.get(key)) for key in ("antecedent_candidates", "ranked_candidates", "selected_owner", "rejected_candidates", "resolution_status")},
        "ownership_resolution": {"segment_provenance": _jsonable(first_provenance.get("segment_provenance", {})), "attribute_ownership": _jsonable(first_provenance.get("resolved_provenance", {}).get("attribute_ownership", {}))},
        "cross_segment_state": {"context_state": _jsonable(first_provenance.get("context_state", {})), "typed_context_state": _jsonable(first_provenance.get("typed_context_state", {}))},
        "resolved_semantics": {"mentions": actuals, "authority": _jsonable(first_provenance.get("resolved_provenance", {}))},
        "generated_relations": {"relations": [item["relations"] for item in actuals]},
        "final_projection": {"mentions": actuals},
        "prediction": {"mentions": actuals},
        "gold": {"mentions": golds},
        "comparison": {"case_id": case.case_id, "mismatch_count": len(mismatches)},
    }


def _build_trace(case: BenchmarkCase, results: list[tuple[GoldMention, Any]], evaluation_id: str) -> ClinicalEvaluationTrace:
    mismatches = _mismatches(results)
    payloads = _snapshot_payloads(case, results, mismatches)
    trace = ClinicalEvaluationTrace.create(
        evaluation_id=evaluation_id,
        case_id=case.case_id,
        corpus_version="D2",
        corpus_checksum=_sha256(OFFICIAL),
        resolver_version=_git_head(),
        resolver_checksum=_resolver_checksum(),
        policy_version="1.3",
        schema_version="v2",
    )
    for stage in STAGE_ORDER:
        changed = [item.semantic_dimension for item in mismatches if item.stage == stage]
        granularity = _granularity(stage, results, mismatches) if stage in {"semantic_candidates", "reference_resolution", "ownership_resolution", "generated_relations", "final_projection"} else {}
        trace = trace.append_snapshot(ClinicalStageSnapshot(
            stage=stage,
            payload=payloads[stage],
            changed_fields=tuple(sorted(set(changed))),
            provenance={
                "trace_capture": "D2_trace_granularity_v2",
                "case_id": case.case_id,
                "stage_source": "adapter_result_provenance" if stage not in {"input_segments", "gold", "comparison"} else "evaluation_boundary",
            },
            granularity=granularity,
        ))
    for mismatch in mismatches:
        trace = trace.add_mismatch(mismatch)
    trace.validate()
    return trace


def _classify(analysis: dict[str, Any]) -> str:
    if analysis.get("status") == "PASS":
        return "PASS"
    stage = analysis.get("first_divergence_stage")
    confidence = float(analysis.get("confidence", 0.0))
    if confidence >= 0.75 and stage in {"local_mentions", "ownership_resolution", "generated_relations", "final_projection"}:
        return "G1"
    if confidence >= 0.75 and stage in {"reference_resolution", "cross_segment_state"}:
        return "G2"
    return "INDETERMINATE"


def _relation_metrics(cases: tuple[BenchmarkCase, ...], result_by_case: dict[str, dict[str, Any]]) -> dict[str, float]:
    relation_total = relation_exact = material_total = material_exact = provenance_total = provenance_exact = 0
    for case in cases:
        finding = result_by_case[case.case_id]
        traces = {item["mention_id"]: item for item in finding["mention_results"]}
        for index, gold in enumerate(case.gold):
            mention = traces[f"m{index + 1}"]
            expected = _expected_relation_records(gold)
            actual_full = mention["relations_full"]
            actual = _semantic_relation_records(actual_full)
            if expected:
                relation_total += 1
                relation_exact += int(expected == actual)
            derived = [item for item in expected if item["relation_type"] in {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "HAS_LATERALITY", "DISCONTINUED_AT"}]
            for relation in derived:
                material_total += 1
                key = (relation["relation_type"], relation["target"], relation.get("value"))
                material_exact += int(any((item.get("relation_type"), item.get("target"), item.get("value")) == key for item in actual_full))
                provenance_total += 1
                matching = next((item for item in actual_full if (item.get("relation_type"), item.get("target"), item.get("value")) == key), None)
                provenance_exact += int(bool(matching and matching.get("source_segment_ids") and matching.get("provenance")))
    return {
        "relation_exact_match": relation_exact / relation_total if relation_total else 1.0,
        "relation_materialization": material_exact / material_total if material_total else 1.0,
        "relation_provenance": provenance_exact / provenance_total if provenance_total else 1.0,
    }


async def _run(cases: tuple[BenchmarkCase, ...], execution_id: str) -> dict[str, Any]:
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    case_records: list[dict[str, Any]] = []
    trace_results: dict[str, dict[str, Any]] = {}
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
        finding = FirstDivergenceAnalyzer().analyze(ClinicalEvaluationTrace.load(trace_path))
        finding["repair_class"] = _classify(finding)
        mention_results = []
        for index, (gold, result) in enumerate(results):
            mention_results.append({"mention_id": f"m{index + 1}", "relations_full": _actual_relation_records(result)})
        trace_results[case.case_id] = {"finding": finding, "mention_results": mention_results}
        case_records.append({"case_id": case.case_id, "trace": str(trace_path), "mention_count": len(results), "mismatch_count": len(trace.mismatches), "trace_schema": "clinical-evaluation-trace/v2"})

    findings = [trace_results[case.case_id]["finding"] for case in cases]
    class_counts = Counter(item["repair_class"] for item in findings if item["status"] == "FAIL")
    stage_counts = Counter(item["first_divergence_stage"] for item in findings if item["status"] == "FAIL")
    dimension_counts = Counter(item["semantic_dimension"] for item in findings if item["status"] == "FAIL")
    mention_total = sum(len(case.gold) for case in cases)
    exact_cases = {case.case_id: trace_results[case.case_id]["finding"]["status"] == "PASS" for case in cases}
    mention_exact = sum(len(case.gold) for case in cases if exact_cases[case.case_id])
    cross_total = sum(len(gold.segment_ids) > 1 for case in cases for gold in case.gold)
    cross_exact = sum(int(exact_cases[case.case_id]) for case in cases for gold in case.gold if len(gold.segment_ids) > 1)
    provenance_ok = sum(1 for case in cases for record in trace_results[case.case_id]["mention_results"] if record["relations_full"] is not None)
    relation = _relation_metrics(cases, trace_results)
    return {
        "status": "D2_DIAGNOSTIC_COMPLETE",
        "execution_id": execution_id,
        "one_shot": True,
        "corpus_version": "D2",
        "official_corpus_checksum": _sha256(OFFICIAL),
        "policy_version": "1.3",
        "policy_checksum": _sha256(POLICY),
        "resolver_version": _git_head(),
        "resolver_checksum": _resolver_checksum(),
        "cases": len(cases),
        "mentions": mention_total,
        "traces": len(case_records),
        "trace_contract": {"schema": "clinical-evaluation-trace/v2", "all_saved": True, "all_valid": True, "stage_count": len(STAGE_ORDER), "granularity_stages": 5, "analyzer_rerun_resolver": False},
        "findings": findings,
        "metrics": {
            "mention_exact_match": mention_exact / mention_total if mention_total else 1.0,
            "cross_segment_resolution": cross_exact / cross_total if cross_total else 1.0,
            "cross_mention_isolation": sum(exact_cases.values()) / len(cases) if cases else 1.0,
            "provenance": provenance_ok / mention_total if mention_total else 1.0,
            **relation,
        },
        "repair_class_counts": {key: class_counts.get(key, 0) for key in ("G1", "G2", "G3", "G4", "INDETERMINATE")},
        "first_divergence_stage_counts": dict(stage_counts),
        "semantic_dimension_counts": dict(dimension_counts),
        "top_root_causes": dimension_counts.most_common(10),
        "case_records": case_records,
        "d1_comparison": json.loads(D1_RESULT.read_text(encoding="utf-8")).get("metrics", {}) if D1_RESULT.exists() else {},
        "resolver_repair": "NOT_AUTHORIZED",
        "d1": "CONSUMED_IMMUTABLE",
        "v7": "CONSUMED_IMMUTABLE",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
    }


def _write_reports(result: dict[str, Any]) -> None:
    ROOT_CAUSE.write_text(json.dumps({
        "status": result["status"],
        "execution_id": result["execution_id"],
        "corpus_checksum": result["official_corpus_checksum"],
        "trace_schema": "clinical-evaluation-trace/v2",
        "repair_class_counts": result["repair_class_counts"],
        "first_divergence_stage_counts": result["first_divergence_stage_counts"],
        "semantic_dimension_counts": result["semantic_dimension_counts"],
        "top_root_causes": result["top_root_causes"],
        "metrics": result["metrics"],
        "findings": result["findings"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# D2 First Divergence Report", "", "Status: **HUMAN GATE**", "", "D2 was executed once with Trace Granularity v2. This report is generated from the saved traces; the analyzer never invokes the resolver.", "", "## Metrics", ""]
    for key, value in result["metrics"].items():
        lines.append(f"- `{key}`: `{value:.6f}`")
    lines.extend(["", "## First divergence stages", ""])
    for key, value in sorted(result["first_divergence_stage_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Findings", ""])
    for finding in result["findings"]:
        if finding["status"] == "PASS":
            continue
        lines.append(f"- `{finding['case_id']}` — `{finding['first_divergence_stage']}` / `{finding['semantic_dimension']}`: `{finding['expected']}` → `{finding['actual']}`; confidence `{finding['confidence']}`; class `{finding.get('repair_class')}`")
    lines.extend(["", "D1 was not rerun. D2 is diagnostic evidence only; no repair is authorized by this result.", ""])
    FIRST_REPORT.write_text("\n".join(lines), encoding="utf-8")
    capability = ["# D2 Capability Classification", "", "Status: **HUMAN GATE**", "", "## Classification", ""]
    for key in ("G1", "G2", "G3", "G4", "INDETERMINATE"):
        capability.append(f"- `{key}`: `{result['repair_class_counts'][key]}`")
    capability.extend(["", "G3 and G4 are not inferred from low scores. This run does not authorize repair, D1/V7 rerun, provider introduction, Shadow Integration, or Production.", "", "## Recommended next milestone", "", "Review the v2 first-divergence matrix and authorize only a focused change supported by preserved evidence.", ""])
    CAPABILITY_REPORT.write_text("\n".join(capability), encoding="utf-8")


def main() -> None:
    if OUTPUT.exists() or EXECUTION_RECORD.exists():
        raise RuntimeError("D2 is one-shot and already has an execution record")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "D2_FROZEN" or not manifest.get("one_shot_authorized"):
        raise RuntimeError("D2 freeze/authorization gate failed")
    if manifest.get("official_corpus_checksum") != _sha256(OFFICIAL):
        raise RuntimeError("D2 corpus checksum mismatch")
    if manifest.get("trace_schema") != "clinical-evaluation-trace/v2":
        raise RuntimeError("D2 trace v2 freeze missing")
    execution_id = f"d2-one-shot-{uuid.uuid4()}"
    record = {
        "status": "STARTED",
        "execution_id": execution_id,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "one_shot": True,
        "official_corpus_checksum": _sha256(OFFICIAL),
        "resolver_checksum": _resolver_checksum(),
        "policy_checksum": _sha256(POLICY),
        "trace_schema": "clinical-evaluation-trace/v2",
        "resolver_repair_after_run": "NOT_AUTHORIZED",
        "d1_rerun": False,
        "v7_rerun": False,
    }
    EXECUTION_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = asyncio.run(_run(_cases(), execution_id))
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finished = dict(record)
    finished.update({"status": result["status"], "finished_at_utc": result["finished_at_utc"], "result": str(OUTPUT), "trace_directory": str(TRACE_DIR), "trace_count": result["traces"]})
    EXECUTION_RECORD.write_text(json.dumps(finished, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"one_shot_run_count": 1, "one_shot_execution_id": execution_id, "one_shot_result_checksum": _sha256(OUTPUT), "trace_directory": str(TRACE_DIR), "trace_count": result["traces"], "status": "D2_CONSUMED"})
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_reports(result)
    print(json.dumps({"status": result["status"], "execution_id": execution_id, "cases": result["cases"], "mentions": result["mentions"], "traces": result["traces"], "metrics": result["metrics"], "repair_class_counts": result["repair_class_counts"], "first_divergence_stage_counts": result["first_divergence_stage_counts"], "outputs": [str(OUTPUT), str(ROOT_CAUSE), str(FIRST_REPORT), str(CAPABILITY_REPORT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
