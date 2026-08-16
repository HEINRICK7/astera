"""Audit D1 relation/prediction boundaries from saved traces only."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from .evaluation_trace import ClinicalEvaluationTrace


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
TRACE_DIR = RESULTS / "d1-traces-2026-08-15"
D1_RESULT = RESULTS / "D1_ONE_SHOT_RESULT.json"
RELATION_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D1_RELATION_BOUNDARY_AUDIT.md"
PREDICTION_REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D1_PREDICTION_BOUNDARY_AUDIT.md"
MATRIX = RESULTS / "D1_RECLASSIFIED_ROOT_CAUSE_MATRIX.json"
RELATION_CATEGORIES = (
    "RELATION_MISSING", "RELATION_EXTRA", "RELATION_WRONG_TYPE",
    "RELATION_WRONG_ENDPOINT", "RELATION_WRONG_VALUE", "RELATION_DUPLICATED",
    "RELATION_HISTORICAL_AS_CURRENT", "ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED",
)
PREDICTION_CATEGORIES = (
    "PREDICTION_FIELD_DROPPED", "PREDICTION_FIELD_DEFAULTED", "PREDICTION_FIELD_TRANSFORMED",
    "PREDICTION_MENTION_DROPPED", "PREDICTION_MENTION_EXTRA", "PREDICTION_RELATION_DROPPED",
    "SERIALIZATION_MISMATCH", "EVALUATOR_CONTRACT_MISMATCH", "TRACE_GRANULARITY_INSUFFICIENT",
)


def _semantic_mentions(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    mentions = []
    for mention in payload.get("mentions", ()):
        relations = [
            {
                "relation_type": relation.get("relation_type"),
                "target": relation.get("target"),
                "value": relation.get("value"),
            }
            for relation in mention.get("relations", ())
            if isinstance(relation, Mapping)
        ]
        mentions.append({
            "surface": mention.get("surface"),
            "fields": mention.get("fields", {}),
            "relations": relations,
        })
    return mentions


def _relation_key(relation: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return (relation.get("relation_type"), relation.get("target"), relation.get("value"))


def _relation_classifications(
    expected: list[dict[str, Any]],
    actual: list[dict[str, Any]],
    resolved_fields: Mapping[str, Any],
) -> list[dict[str, Any]]:
    # Gold snapshots may carry an explicit lifecycle relation plus the
    # contract's derived relation. Relation equality is set-semantic here;
    # duplicate expected records must not be misclassified as an actual
    # materialization defect.
    expected_counts = Counter(set(_relation_key(item) for item in expected))
    actual_counts = Counter(_relation_key(item) for item in actual)
    findings: list[dict[str, Any]] = []

    for key, count in expected_counts.items():
        if actual_counts[key] >= count:
            continue
        relation_type, target, value = key
        missing_count = count - actual_counts[key]
        derived_field = {
            "HAS_DOSE": "dose",
            "HAS_FREQUENCY": "frequency",
            "HAS_ROUTE": "route",
            "HAS_LATERALITY": "laterality",
            "DISCONTINUED_AT": "status",
        }.get(relation_type)
        if derived_field and resolved_fields.get(derived_field) is not None:
            category = "ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED"
        else:
            category = "RELATION_MISSING"
        findings.append({"category": category, "relation": {"relation_type": relation_type, "target": target, "value": value}, "count": missing_count})

    for key, count in actual_counts.items():
        if count > 1:
            findings.append({"category": "RELATION_DUPLICATED", "relation": {"relation_type": key[0], "target": key[1], "value": key[2]}, "count": count - 1})
        if expected_counts[key] >= count:
            continue
        relation_type, target, value = key
        category = "RELATION_EXTRA"
        if any(item[0] != relation_type and item[1:] == key[1:] for item in expected_counts):
            category = "RELATION_WRONG_TYPE"
        elif any(item[0] == relation_type and item[1] != target and item[2] == value for item in expected_counts):
            category = "RELATION_WRONG_ENDPOINT"
        elif any(item[:2] == key[:2] and item[2] != value for item in expected_counts):
            category = "RELATION_WRONG_VALUE"
        findings.append({"category": category, "relation": {"relation_type": relation_type, "target": target, "value": value}, "count": count - expected_counts[key]})
    return findings


def _prediction_boundary(final_payload: Mapping[str, Any], prediction_payload: Mapping[str, Any], gold_payload: Mapping[str, Any]) -> dict[str, Any]:
    final_mentions = _semantic_mentions(final_payload)
    prediction_mentions = _semantic_mentions(prediction_payload)
    gold_mentions = _semantic_mentions(gold_payload)
    if final_mentions == prediction_mentions:
        if final_mentions == gold_mentions:
            return {"category": "NO_BOUNDARY_MISMATCH", "confidence": 1.0, "details": {}}
        return {
            "category": "TRACE_GRANULARITY_INSUFFICIENT",
            "confidence": 0.9,
            "details": {
                "final_projection_matches_prediction": True,
                "final_projection_matches_gold": False,
                "prediction_matches_gold": False,
                "cause_not_attributable_to_projection_prediction_boundary": True,
            },
        }
    if len(final_mentions) > len(prediction_mentions):
        category = "PREDICTION_MENTION_DROPPED"
    elif len(final_mentions) < len(prediction_mentions):
        category = "PREDICTION_MENTION_EXTRA"
    else:
        category = "SERIALIZATION_MISMATCH"
    return {"category": category, "confidence": 0.95, "details": {"final_mentions": final_mentions, "prediction_mentions": prediction_mentions}}


def main() -> None:
    result = json.loads(D1_RESULT.read_text(encoding="utf-8"))
    relation_cases = [item for item in result["findings"] if item.get("first_divergence_stage") == "generated_relations"]
    prediction_cases = [item for item in result["findings"] if item.get("first_divergence_stage") == "prediction"]
    relation_findings: list[dict[str, Any]] = []
    prediction_findings: list[dict[str, Any]] = []
    relation_case_ids = {item["case_id"] for item in relation_cases}
    for finding in relation_cases + prediction_cases:
        trace = ClinicalEvaluationTrace.load(next(item["trace"] for item in result["case_records"] if item["case_id"] == finding["case_id"]))
        snapshots = {snapshot.stage: snapshot for snapshot in trace.snapshots}
        if finding["case_id"] in relation_case_ids:
            gold_mentions = snapshots["gold"].payload["mentions"]
            resolved_mentions = snapshots["resolved_semantics"].payload["mentions"]
            generated_relations = snapshots["generated_relations"].payload.get("relations", [])
            for index, gold in enumerate(gold_mentions):
                expected = gold.get("relations", [])
                actual = generated_relations[index] if index < len(generated_relations) else []
                resolved_fields = resolved_mentions[index].get("fields", {}) if index < len(resolved_mentions) else {}
                for item in _relation_classifications(expected, actual, resolved_fields):
                    relation_findings.append({"case_id": finding["case_id"], "mention_index": index, "first_divergence_stage": "generated_relations", **item, "repair_class": "G1"})
        else:
            boundary = _prediction_boundary(snapshots["final_projection"].payload, snapshots["prediction"].payload, snapshots["gold"].payload)
            prediction_findings.append({"case_id": finding["case_id"], "first_divergence_stage": "prediction", **boundary, "repair_class": "G1" if boundary["category"] in {"PREDICTION_MENTION_DROPPED", "PREDICTION_MENTION_EXTRA", "SERIALIZATION_MISMATCH", "PREDICTION_FIELD_DROPPED", "PREDICTION_FIELD_DEFAULTED", "PREDICTION_FIELD_TRANSFORMED"} else "INDETERMINATE"})

    relation_counts = Counter(item["category"] for item in relation_findings)
    prediction_counts = Counter(item["category"] for item in prediction_findings)
    relation_lines = ["# D1 Relation Boundary Audit", "", "Status: **HUMAN GATE**", "", "Audited only the persisted D1 traces. D1 was not rerun.", "", "## Classification counts", ""]
    relation_counts_complete = {category: relation_counts.get(category, 0) for category in RELATION_CATEGORIES}
    for category, count in sorted(relation_counts_complete.items(), key=lambda item: (-item[1], item[0])):
        relation_lines.append(f"- `{category}`: `{count}`")
    relation_lines.extend(["", "## Findings", ""])
    for finding in relation_findings:
        relation_lines.append(f"- `{finding['case_id']}` mention `{finding['mention_index']}` — `{finding['category']}`: `{finding['relation']}`; count `{finding['count']}`; repair class `{finding['repair_class']}`")
    relation_lines.extend(["", "Interpretation: a missing derived relation with its attribute already present in `resolved_semantics` is a relation materialization G1. No reference or ownership failure is assigned without trace evidence.", ""])
    RELATION_REPORT.write_text("\n".join(relation_lines), encoding="utf-8")

    prediction_lines = ["# D1 Prediction Boundary Audit", "", "Status: **HUMAN GATE**", "", "Audited only the persisted D1 traces. D1 was not rerun.", "", "## Classification counts", ""]
    prediction_counts_complete = {category: prediction_counts.get(category, 0) for category in PREDICTION_CATEGORIES}
    for category, count in sorted(prediction_counts_complete.items(), key=lambda item: (-item[1], item[0])):
        prediction_lines.append(f"- `{category}`: `{count}`")
    prediction_lines.extend(["", "## Findings", ""])
    for finding in prediction_findings:
        prediction_lines.append(f"- `{finding['case_id']}` — `{finding['category']}`; confidence `{finding['confidence']}`; repair class `{finding['repair_class']}`")
    prediction_lines.extend(["", "All cases where `final_projection` equals `prediction` but both differ from gold are `TRACE_GRANULARITY_INSUFFICIENT`; the saved trace cannot prove a prediction mapping bug.", ""])
    PREDICTION_REPORT.write_text("\n".join(prediction_lines), encoding="utf-8")

    indeterminate = sum(item["repair_class"] == "INDETERMINATE" for item in prediction_findings)
    matrix = {
        "status": "HUMAN_GATE",
        "source_execution_id": result["execution_id"],
        "source_trace_directory": str(TRACE_DIR),
        "rerun_performed": False,
        "repair_performed": False,
        "relation_first_divergence_cases": len(relation_cases),
        "prediction_first_divergence_cases": len(prediction_cases),
        "relation_finding_count": len(relation_findings),
        "relation_findings": relation_findings,
        "prediction_findings": prediction_findings,
        "relation_category_counts": relation_counts_complete,
        "prediction_category_counts": prediction_counts_complete,
        "relation_materialization_bugs": sum(item["category"] == "ATTRIBUTE_AVAILABLE_BUT_RELATION_NOT_MATERIALIZED" for item in relation_findings),
        "relation_boundary_g1_findings": sum(item["repair_class"] == "G1" for item in relation_findings),
        "confirmed_g1_cases": len(relation_cases),
        "prediction_mapping_bugs": sum(item["repair_class"] == "G1" for item in prediction_findings),
        "evaluator_contract_bugs": sum(item["category"] == "EVALUATOR_CONTRACT_MISMATCH" for item in prediction_findings),
        "trace_insufficient_cases": sum(item["category"] == "TRACE_GRANULARITY_INSUFFICIENT" for item in prediction_findings),
        "confirmed_class_counts": {"G1": len(relation_findings) + sum(item["repair_class"] == "G1" for item in prediction_findings), "G2": 0, "G3": 0, "G4": 0},
        "still_indeterminate": indeterminate,
        "classification_guard": "G3/G4 not inferred; no provider decision authorized",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
    }
    MATRIX.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": matrix["status"], "relation_counts": relation_counts_complete, "prediction_counts": prediction_counts_complete, "summary": {key: matrix[key] for key in ("relation_materialization_bugs", "prediction_mapping_bugs", "evaluator_contract_bugs", "trace_insufficient_cases", "confirmed_g1_cases", "confirmed_class_counts", "still_indeterminate")}, "outputs": [str(RELATION_REPORT), str(PREDICTION_REPORT), str(MATRIX)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
