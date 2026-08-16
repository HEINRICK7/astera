"""Apply the human-approved V6 semantic policy decisions to the audit findings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DEFAULT_INPUT = ROOT / "results" / "v6-resolved-gold-alignment-audit-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "v6-semantic-policy-adjudication-2026-08-15.json"


def _adjudication_for(finding: dict[str, Any]) -> dict[str, Any] | None:
    if finding.get("classification") == "MISSING_RELATION" and finding.get("relation", [None])[0] == "DISCONTINUED_AT":
        return {
            "decision": "APPROVE",
            "policy_ids": ["SEM-STATUS-001", "SEM-REL-001"],
            "policy_version": "1.0",
            "approver": "Carlos Henrique",
            "decision_id": "D-REL-001",
        }
    if (
        finding.get("classification") == "WRONG_STATUS"
        and finding.get("expected") in {"present", "historical"}
        and finding.get("resolved") is None
    ):
        return {
            "decision": "APPROVE",
            "policy_ids": ["SEM-STATUS-001"],
            "policy_version": "1.0",
            "approver": "Carlos Henrique",
            "decision_id": "D-STATUS-001",
        }
    if (
        finding.get("classification") == "WRONG_STATUS"
        and finding.get("expected") is None
        and finding.get("resolved") == "confirmed"
    ):
        return {
            "decision": "REJECT",
            "policy_ids": ["SEM-STATUS-001"],
            "policy_version": "1.0",
            "approver": "Carlos Henrique",
            "decision_id": "D-STATE-001",
        }
    return None


def run(input_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        if existing.get("run_type") != "v6-semantic-policy-adjudication":
            raise RuntimeError(f"refusing to overwrite non-adjudication result: {output_path}")
    source = json.loads(input_path.read_text(encoding="utf-8"))
    result = json.loads(json.dumps(source, ensure_ascii=False))
    applied = 0
    unresolved_review_items = 0
    applied_by_decision: dict[str, int] = {"D-STATUS-001": 0, "D-REL-001": 0, "D-STATE-001": 0}

    for record in result["records"]:
        for finding in record["differing_fields"]:
            adjudication = _adjudication_for(finding)
            if adjudication is None:
                if finding.get("gold_review_required"):
                    unresolved_review_items += 1
                continue
            finding["pre_adjudication_error_type"] = finding.get("error_type")
            finding["error_type"] = "A"
            finding["gold_review_required"] = False
            finding["adjudication"] = adjudication
            applied += 1
            applied_by_decision[adjudication["decision_id"]] += 1

    counts: dict[str, int] = {}
    for record in result["records"]:
        for finding in record["differing_fields"]:
            classification = finding["classification"]
            counts[classification] = counts.get(classification, 0) + 1
    type_counts = {"A": 0, "B": 0, "C": 0}
    for record in result["records"]:
        for finding in record["differing_fields"]:
            type_counts[finding["error_type"]] += 1

    result["status"] = "semantic_policy_adjudicated"
    result["run_type"] = "v6-semantic-policy-adjudication"
    result["policy_version"] = "1.0"
    result["policy_approver"] = "Carlos Henrique"
    result["gold_modified"] = False
    result["corpus_modified"] = False
    result["resolver_modified"] = False
    result["adjudication"] = {
        "decisions": ["D-STATUS-001", "D-REL-001", "D-STATE-001"],
        "items_considered": 47,
        "items_applied": applied,
        "items_remaining_unresolved": unresolved_review_items,
        "applied_by_decision": applied_by_decision,
        "adjudicated_queue_type_c": 0 if applied == 47 and unresolved_review_items == 0 else unresolved_review_items,
        "residual_type_c_outside_adjudicated_queue": type_counts["C"],
    }
    result["summary"] = {
        "records_with_divergence": len(result["records"]),
        "field_and_relation_findings": sum(counts.values()),
        "classification_counts": counts,
        "error_type_counts": type_counts,
        "type_a": type_counts["A"],
        "type_b": type_counts["B"],
        "type_c": type_counts["C"],
        "gold_review_required": unresolved_review_items,
    }
    result["gold_review_queue"] = []
    result["holdout_evaluation"] = "NOT_EXECUTED"
    result["repair_authorized"] = type_counts["C"] == 0 and unresolved_review_items == 0
    result["next_step"] = "repair-v4-type-a-only" if result["repair_authorized"] else "resolve-residual-type-c-policy"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
