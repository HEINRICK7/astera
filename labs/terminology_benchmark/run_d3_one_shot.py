"""Execute the frozen D3 relation diagnostic exactly once.

The runner invokes the frozen resolver candidate once per gold mention, saves
Trace Granularity v2 snapshots, and performs first-divergence analysis from
those saved traces. It never repairs the resolver or reruns consumed sets.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
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
    _classify,
    _gold_record,
    _granularity,
    _jsonable,
    _mismatches,
    _resolver_checksum,
    _semantic_relation_records,
    _snapshot_payloads,
)


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
OFFICIAL = DATA / "d3_relation_generalization_official.jsonl"
MANIFEST = RESULTS / "D3_FREEZE_MANIFEST.json"
EXECUTION_RECORD = RESULTS / "d3-one-shot-execution-record-2026-08-15.json"
TRACE_DIR = RESULTS / "d3-traces-2026-08-15"
OUTPUT = RESULTS / "D3_ONE_SHOT_RESULT.json"
ROOT_CAUSE = RESULTS / "D3_ROOT_CAUSE_MATRIX.json"
FIRST_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D3_FIRST_DIVERGENCE_REPORT.md"
COMPILER_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D3_RELATION_COMPILER_GENERALIZATION_REPORT.md"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
COMPILER = ROOT / "clinical_projection.py"

DERIVED_TYPES = {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "HAS_LATERALITY", "DISCONTINUED_AT"}
TRANSITION_TYPES = {"CHANGED_FROM", "CHANGED_TO"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    try:
        import subprocess

        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
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
            source="d3-official-frozen",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        )
        for record in records
    )


def _expected_relations(gold: GoldMention) -> list[dict[str, Any]]:
    relations = [{"relation_type": item.relation_type, "target": item.target, "value": item.value} for item in gold.relations]
    if gold.dose:
        relations.append({"relation_type": "HAS_DOSE", "target": "dose", "value": gold.dose})
    if gold.frequency:
        relations.append({"relation_type": "HAS_FREQUENCY", "target": "frequency", "value": gold.frequency})
    if gold.route:
        relations.append({"relation_type": "HAS_ROUTE", "target": "route", "value": gold.route})
    if gold.laterality:
        relations.append({"relation_type": "HAS_LATERALITY", "target": "laterality", "value": gold.laterality})
    if gold.status == "discontinued":
        relations.append({"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"})
    return _semantic_relation_records(relations)


def _actual_relations(result: Any) -> list[dict[str, Any]]:
    return _jsonable(result.provenance.get("projection", {}).get("relations", []))


def _build_trace(case: BenchmarkCase, results: list[tuple[GoldMention, Any]], execution_id: str) -> ClinicalEvaluationTrace:
    mismatches = _mismatches(results)
    payloads = _snapshot_payloads(case, results, mismatches)
    trace = ClinicalEvaluationTrace.create(
        evaluation_id=execution_id,
        case_id=case.case_id,
        corpus_version="D3",
        corpus_checksum=_sha256(OFFICIAL),
        resolver_version=_git_head(),
        resolver_checksum=_resolver_checksum(),
        policy_version="1.3",
        schema_version="v2",
    )
    for stage in STAGE_ORDER:
        changed = [item.semantic_dimension for item in mismatches if item.stage == stage]
        detail = _granularity(stage, results, mismatches) if stage in {"semantic_candidates", "reference_resolution", "ownership_resolution", "generated_relations", "final_projection"} else {}
        trace = trace.append_snapshot(ClinicalStageSnapshot(
            stage=stage,
            payload=payloads[stage],
            changed_fields=tuple(sorted(set(changed))),
            provenance={
                "trace_capture": "D3_trace_granularity_v2",
                "case_id": case.case_id,
                "stage_source": "adapter_result_provenance" if stage not in {"input_segments", "gold", "comparison"} else "evaluation_boundary",
            },
            granularity=detail,
        ))
    for mismatch in mismatches:
        trace = trace.add_mismatch(mismatch)
    trace.validate()
    return trace


def _mention_exact(gold: GoldMention, result: Any) -> bool:
    return all(getattr(result, field) == getattr(gold, field) for field in FIELDS) and _expected_relations(gold) == _semantic_relation_records(_actual_relations(result))


def _matching(actual: list[dict[str, Any]], expected: dict[str, Any]) -> dict[str, Any] | None:
    key = (expected["relation_type"], expected["target"], expected.get("value"))
    return next((item for item in actual if (item.get("relation_type"), item.get("target"), item.get("value")) == key), None)


def _relation_metrics(cases: tuple[BenchmarkCase, ...], result_map: dict[str, list[tuple[GoldMention, Any]]]) -> dict[str, float]:
    relation_total = relation_exact = material_total = material_exact = 0
    owner_total = owner_exact = endpoint_total = endpoint_exact = 0
    current_total = current_exact = transition_total = transition_exact = 0
    provenance_total = provenance_exact = 0
    for case in cases:
        for gold, result in result_map[case.case_id]:
            expected = _expected_relations(gold)
            actual = _actual_relations(result)
            if expected:
                relation_total += 1
                relation_exact += int(expected == _semantic_relation_records(actual))
            for item in expected:
                relation_type = item["relation_type"]
                match = _matching(actual, item)
                if relation_type in DERIVED_TYPES:
                    material_total += 1
                    material_exact += int(match is not None)
                endpoint_total += 1
                endpoint_exact += int(any(row.get("relation_type") == relation_type and row.get("target") == item["target"] for row in actual))
                expected_sources = set(gold.relation_provenance.get(relation_type, ())) or set(gold.attribute_provenance.get(item["target"], ())) or set(gold.segment_ids)
                owner_total += 1
                owner_exact += int(bool(match and match.get("source_mention_id") and set(match.get("source_segment_ids", ())) & expected_sources))
                provenance_total += 1
                provenance_exact += int(bool(match and match.get("source_segment_ids") and match.get("provenance")))
                if relation_type in DERIVED_TYPES:
                    current_total += 1
                    current_exact += int(match is not None and str(match.get("value")) == str(item.get("value")))
                if relation_type in TRANSITION_TYPES:
                    transition_total += 1
                    transition_exact += int(match is not None)
    return {
        "relation_exact_match": relation_exact / relation_total if relation_total else 1.0,
        "relation_materialization": material_exact / material_total if material_total else 1.0,
        "relation_owner_accuracy": owner_exact / owner_total if owner_total else 1.0,
        "relation_endpoint_accuracy": endpoint_exact / endpoint_total if endpoint_total else 1.0,
        "current_vs_historical_accuracy": current_exact / current_total if current_total else 1.0,
        "transition_compilation_accuracy": transition_exact / transition_total if transition_total else 1.0,
        "relation_provenance_accuracy": provenance_exact / provenance_total if provenance_total else 1.0,
    }


async def _execute(cases: tuple[BenchmarkCase, ...], execution_id: str) -> dict[str, Any]:
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    results_by_case: dict[str, list[tuple[GoldMention, Any]]] = {}
    findings: list[dict[str, Any]] = []
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
        results_by_case[case.case_id] = results
        trace = _build_trace(case, results, execution_id)
        trace_path = TRACE_DIR / f"{case.case_id}.json"
        trace.save(trace_path)
        finding = FirstDivergenceAnalyzer().analyze(ClinicalEvaluationTrace.load(trace_path))
        finding["repair_class"] = _classify(finding)
        findings.append(finding)
        records.append({"case_id": case.case_id, "trace": str(trace_path), "mention_count": len(results), "mismatch_count": len(trace.mismatches), "trace_schema": "clinical-evaluation-trace/v2"})

    mention_total = sum(len(case.gold) for case in cases)
    exact_mentions = sum(_mention_exact(gold, result) for results in results_by_case.values() for gold, result in results)
    cross_mentions = [(gold, result) for results in results_by_case.values() for gold, result in results if len(gold.segment_ids) > 1]
    cross_exact = sum(_mention_exact(gold, result) for gold, result in cross_mentions)
    relation = _relation_metrics(cases, results_by_case)
    stage_counts = Counter(item["first_divergence_stage"] for item in findings if item["status"] == "FAIL")
    dimension_counts = Counter(item["semantic_dimension"] for item in findings if item["status"] == "FAIL")
    classes = Counter(item["repair_class"] for item in findings if item["status"] == "FAIL")
    return {
        "status": "D3_DIAGNOSTIC_COMPLETE",
        "execution_id": execution_id,
        "one_shot": True,
        "corpus_version": "D3",
        "official_corpus_checksum": _sha256(OFFICIAL),
        "policy_version": "1.3",
        "policy_checksum": _sha256(POLICY),
        "compiler_checksum": _sha256(COMPILER),
        "resolver_checksum": _resolver_checksum(),
        "trace_schema": "clinical-evaluation-trace/v2",
        "cases": len(cases),
        "mentions": mention_total,
        "traces": len(records),
        "trace_contract": {"all_saved": True, "all_valid": True, "stage_count": len(STAGE_ORDER), "analyzer_rerun_resolver": False},
        "metrics": {
            "mention_exact_match": exact_mentions / mention_total if mention_total else 1.0,
            "cross_segment_resolution": cross_exact / len(cross_mentions) if cross_mentions else 1.0,
            "cross_mention_isolation": sum(_mention_exact(gold, result) for case in cases for gold, result in results_by_case[case.case_id]) / mention_total if mention_total else 1.0,
            "provenance": sum(bool(result.provenance) for results in results_by_case.values() for _, result in results) / mention_total if mention_total else 1.0,
            **relation,
        },
        "findings": findings,
        "repair_class_counts": {key: classes.get(key, 0) for key in ("G1", "G2", "G3", "G4", "INDETERMINATE")},
        "first_divergence_stage_counts": dict(stage_counts),
        "semantic_dimension_counts": dict(dimension_counts),
        "top_root_causes": dimension_counts.most_common(10),
        "historical_relation_comparison": {"D1": 0.1765, "D2": 0.1333},
        "resolver_repair": "NOT_AUTHORIZED",
        "d1": "CONSUMED_IMMUTABLE",
        "d2": "CONSUMED_IMMUTABLE",
        "v7": "CONSUMED_IMMUTABLE",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
        "case_records": records,
    }


def _write_reports(result: dict[str, Any]) -> None:
    ROOT_CAUSE.write_text(json.dumps({
        "status": "HUMAN_GATE",
        "execution_id": result["execution_id"],
        "corpus_checksum": result["official_corpus_checksum"],
        "trace_schema": result["trace_schema"],
        "repair_class_counts": result["repair_class_counts"],
        "first_divergence_stage_counts": result["first_divergence_stage_counts"],
        "semantic_dimension_counts": result["semantic_dimension_counts"],
        "metrics": result["metrics"],
        "findings": result["findings"],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# D3 First Divergence Report", "", "Status: **HUMAN GATE**", "", "D3 was executed once. Findings were produced from persisted Trace Granularity v2 snapshots; no resolver rerun occurred.", "", "## Metrics", ""]
    for key, value in result["metrics"].items():
        lines.append(f"- `{key}`: `{value:.6f}`")
    lines += ["", "## First divergence stages", ""]
    for key, value in sorted(result["first_divergence_stage_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{key}`: `{value}`")
    lines += ["", "## Classification", ""]
    for key, value in result["repair_class_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines += ["", "No repair is authorized from this diagnostic result. D1, D2 and V7 remain consumed and immutable.", ""]
    FIRST_REPORT.write_text("\n".join(lines), encoding="utf-8")

    relation = result["metrics"]
    compiler_lines = [
        "# D3 Relation Compiler Generalization Report", "", "Status: **HUMAN GATE**", "",
        "## One-shot comparison", "",
        f"- D1 relation exact (historical): `{result['historical_relation_comparison']['D1']:.4f}`",
        f"- D2 relation exact (historical): `{result['historical_relation_comparison']['D2']:.4f}`",
        f"- D3 relation exact: `{relation['relation_exact_match']:.4f}`",
        "",
        "## Compiler-specific metrics", "",
    ]
    for key in ("relation_materialization", "relation_owner_accuracy", "relation_endpoint_accuracy", "current_vs_historical_accuracy", "transition_compilation_accuracy", "relation_provenance_accuracy"):
        compiler_lines.append(f"- `{key}`: `{relation[key]:.6f}`")
    compiler_lines += ["", "The D3 corpus is disjoint from prior diagnostic corpora. D3 is evidence only; no repair, rerun or production promotion is authorized.", ""]
    COMPILER_REPORT.write_text("\n".join(compiler_lines), encoding="utf-8")


def main() -> None:
    if OUTPUT.exists() or EXECUTION_RECORD.exists():
        raise RuntimeError("D3 is one-shot and already has an execution record")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("status") != "D3_FROZEN" or not manifest.get("one_shot_authorized"):
        raise RuntimeError("D3 freeze/authorization gate failed")
    if manifest.get("official_corpus_checksum") != _sha256(OFFICIAL):
        raise RuntimeError("D3 corpus checksum mismatch")
    if manifest.get("trace_schema") != "clinical-evaluation-trace/v2":
        raise RuntimeError("D3 trace v2 freeze missing")
    execution_id = f"d3-one-shot-{uuid.uuid4()}"
    record = {
        "status": "STARTED",
        "execution_id": execution_id,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "one_shot": True,
        "official_corpus_checksum": _sha256(OFFICIAL),
        "compiler_checksum": _sha256(COMPILER),
        "resolver_checksum": _resolver_checksum(),
        "policy_checksum": _sha256(POLICY),
        "trace_schema": "clinical-evaluation-trace/v2",
        "resolver_repair_after_run": "NOT_AUTHORIZED",
        "d1_rerun": False,
        "d2_rerun": False,
        "v7_rerun": False,
    }
    EXECUTION_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = asyncio.run(_execute(_cases(), execution_id))
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finished = dict(record)
    finished.update({"status": result["status"], "finished_at_utc": result["finished_at_utc"], "result": str(OUTPUT), "trace_directory": str(TRACE_DIR), "trace_count": result["traces"]})
    EXECUTION_RECORD.write_text(json.dumps(finished, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"one_shot_run_count": 1, "one_shot_execution_id": execution_id, "one_shot_result_checksum": _sha256(OUTPUT), "trace_directory": str(TRACE_DIR), "trace_count": result["traces"], "status": "D3_CONSUMED"})
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_reports(result)
    print(json.dumps({"status": result["status"], "execution_id": execution_id, "cases": result["cases"], "mentions": result["mentions"], "traces": result["traces"], "metrics": result["metrics"], "repair_class_counts": result["repair_class_counts"], "first_divergence_stage_counts": result["first_divergence_stage_counts"], "outputs": [str(OUTPUT), str(ROOT_CAUSE), str(FIRST_REPORT), str(COMPILER_REPORT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
