"""Recompute D4 relation metadata metrics from frozen traces only.

This is an offline analysis correction. It never imports or executes the
resolver and never changes the consumed D4 corpus or traces.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from .evaluation_trace import ClinicalEvaluationTrace
from .run_d4_one_shot import (
    COMPILER,
    FIRST_REPORT,
    GENERALIZATION_REPORT,
    MANIFEST,
    OFFICIAL,
    OUTPUT,
    POLICY,
    ROOT_CAUSE,
    SIGNAL_REPORT,
    _actual_relations,
    _expected_relations,
    _gold,
    _raw_records,
    _sha256,
)


def _rich_provenance(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _metric(result: dict[str, Any]) -> dict[str, float]:
    cases = [json.loads(line) for line in OFFICIAL.read_text(encoding="utf-8").splitlines() if line.strip()]
    case_by_id = {item["case_id"]: item for item in cases}
    relation_total = relation_exact = material_total = material_exact = owner_total = owner_exact = endpoint_total = endpoint_exact = current_total = current_exact = transition_total = transition_exact = provenance_total = provenance_exact = 0
    mention_total = mention_exact = cross_total = cross_exact = 0
    for case_id, trace_path in ((item["case_id"], Path(item["trace"])) for item in result["case_records"]):
        case = case_by_id[case_id]
        trace = ClinicalEvaluationTrace.load(trace_path)
        prediction = next(item for item in trace.snapshots if item.stage == "prediction").payload
        actual_mentions = prediction["mentions"]
        for index, gold_item in enumerate(case["gold"]):
            gold = _gold(gold_item)
            actual = actual_mentions[index]
            expected = _expected_relations(gold)
            semantic_actual = [dict(item) for item in actual.get("relations", [])]
            rich = _rich_provenance(actual.get("provenance"))
            full_actual = rich.get("projection", {}).get("relations", [])
            if expected:
                relation_total += 1
                relation_exact += int(expected == semantic_actual)
            mention_total += 1
            mention_is_exact = all(actual.get("fields", {}).get(field) == getattr(gold, field) for field in ("negated", "certainty", "temporality", "experiencer", "laterality", "dose", "dose_value", "dose_unit", "frequency", "route", "status")) and expected == semantic_actual
            mention_exact += int(mention_is_exact)
            if len(gold.segment_ids) > 1:
                cross_total += 1
                cross_exact += int(mention_is_exact)
            for item in expected:
                match = next((row for row in full_actual if (row.get("relation_type"), row.get("target"), row.get("value")) == (item["relation_type"], item["target"], item.get("value"))), None)
                if item["relation_type"] in {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "HAS_LATERALITY", "DISCONTINUED_AT"}:
                    material_total += 1
                    material_exact += int(match is not None)
                endpoint_total += 1
                endpoint_exact += int(any(row.get("relation_type") == item["relation_type"] and row.get("target") == item["target"] for row in full_actual))
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
    updated = dict(result["metrics"])
    updated.update({
        "relation_exact_match": div(relation_exact, relation_total),
        "relation_materialization": div(material_exact, material_total),
        "relation_owner_accuracy": div(owner_exact, owner_total),
        "relation_endpoint_accuracy": div(endpoint_exact, endpoint_total),
        "current_vs_historical_accuracy": div(current_exact, current_total),
        "transition_compilation_accuracy": div(transition_exact, transition_total),
        "relation_provenance_accuracy": div(provenance_exact, provenance_total),
        "mention_exact_match": mention_exact / mention_total if mention_total else 1.0,
        "cross_segment_resolution": cross_exact / cross_total if cross_total else 1.0,
    })
    result["metrics"] = updated
    result["offline_reanalysis"] = {"performed": True, "source": "persisted D4 Trace v2 snapshots", "resolver_rerun": False, "reason": "restored relation metadata from serialized provenance for owner/provenance metrics"}
    return updated


def main() -> None:
    result = json.loads(OUTPUT.read_text(encoding="utf-8"))
    metrics = _metric(result)
    result["c2_gate"] = "PASS" if metrics["relation_input_owner_completeness"] >= 0.90 and metrics["relation_input_state_completeness"] >= 0.90 and metrics["transition_contract_validity"] >= 0.90 and metrics["relation_input_provenance"] == 1.0 and metrics["silent_invalid_relation_creation"] == 0 else "FAIL"
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    matrix = json.loads(ROOT_CAUSE.read_text(encoding="utf-8"))
    matrix["metrics"] = metrics
    matrix["offline_reanalysis"] = result["offline_reanalysis"]
    ROOT_CAUSE.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = SIGNAL_REPORT.read_text(encoding="utf-8").splitlines()
    replacements = {
        "relation_exact_match": metrics["relation_exact_match"],
        "relation_materialization": metrics["relation_materialization"],
        "relation_owner_accuracy": metrics["relation_owner_accuracy"],
        "relation_endpoint_accuracy": metrics["relation_endpoint_accuracy"],
        "current_vs_historical_accuracy": metrics["current_vs_historical_accuracy"],
        "transition_compilation_accuracy": metrics["transition_compilation_accuracy"],
        "relation_provenance_accuracy": metrics["relation_provenance_accuracy"],
        "mention_exact_match": metrics["mention_exact_match"],
        "cross_segment_resolution": metrics["cross_segment_resolution"],
    }
    for index, line in enumerate(lines):
        for key, value in replacements.items():
            if line.startswith(f"- `{key}`:"):
                lines[index] = f"- `{key}`: `{value:.6f}`"
    lines.insert(4, "Offline reanalysis: **performed from persisted traces; resolver rerun = false**")
    SIGNAL_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    gate_lines = GENERALIZATION_REPORT.read_text(encoding="utf-8").splitlines()
    gate_lines.insert(4, "Relation metadata metrics were corrected offline from serialized provenance; no D4 rerun occurred.")
    GENERALIZATION_REPORT.write_text("\n".join(gate_lines) + "\n", encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["one_shot_result_checksum"] = _sha256(OUTPUT)
    manifest["offline_reanalysis"] = result["offline_reanalysis"]
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": metrics, "c2_gate": result["c2_gate"], "resolver_rerun": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
