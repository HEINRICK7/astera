"""Apply human adjudication to the 19 residual V6 Type C findings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DEFAULT_INPUT = ROOT / "results" / "v6-semantic-policy-adjudication-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "v6-residual-type-c-adjudication-2026-08-15.json"


def _decision(record: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any] | None:
    case_id = record["case_id"]
    surface = record["surface"]
    classification = finding["classification"]

    if classification == "WRONG_TEMPORALITY":
        gold_issue = {
            ("v6-r-003-3", "enjoo"),
            ("v6-r-003-3", "azia"),
            ("v6-r-008-3", "febre"),
            ("v6-r-008-3", "dor no corpo"),
            ("v6-c-001-1", "tontura"),
            ("v6-c-001-2", "tontura"),
            ("v6-c-001-3", "tontura"),
            ("v6-c-002-1", "mãe"),
            ("v6-c-002-2", "mãe"),
            ("v6-c-002-3", "mãe"),
        }
        if (case_id, surface) in gold_issue:
            return {
                "decision": "APPROVE_POLICY_GOLD_REVIEW",
                "error_type": "B",
                "policy_ids": ["SEM-TEMP-001"],
                "policy_version": "1.1",
                "approver": "Carlos Henrique",
                "decision_id": "D-TEMP-001",
                "gold_review_required": True,
                "reason": "gold temporality conflicts with event-time policy; do not train resolver to imitate it",
            }
        return {
            "decision": "APPROVE_RESOLVER_REPAIR",
            "error_type": "A",
            "policy_ids": ["SEM-TEMP-001"],
            "policy_version": "1.1",
            "approver": "Carlos Henrique",
            "decision_id": "D-TEMP-001",
            "gold_review_required": False,
            "reason": "explicit historical event was resolved as current",
        }

    if classification == "WRONG_FREQUENCY":
        return {
            "decision": "APPROVE_RESOLVER_REPAIR",
            "error_type": "A",
            "policy_ids": ["SEM-FREQ-001"],
            "policy_version": "1.1",
            "approver": "Carlos Henrique",
            "decision_id": "D-FREQ-001",
            "gold_review_required": False,
            "reason": "explicit transition retained historical frequency as current",
        }

    if classification == "EXTRA_RELATION":
        return {
            "decision": "APPROVE_RESOLVER_REPAIR",
            "error_type": "A",
            "policy_ids": ["SEM-REL-002"],
            "policy_version": "1.1",
            "approver": "Carlos Henrique",
            "decision_id": "D-REL-EXTRA-001",
            "gold_review_required": False,
            "reason": "historical value must not be projected as an ordinary current HAS_* relation",
        }
    return None


def run(input_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
        if existing.get("run_type") != "v6-residual-type-c-adjudication":
            raise RuntimeError(f"refusing to overwrite non-adjudication result: {output_path}")
    source = json.loads(input_path.read_text(encoding="utf-8"))
    result = json.loads(json.dumps(source, ensure_ascii=False))
    applied = 0
    review_queue: list[dict[str, Any]] = []
    by_decision = {"D-TEMP-001": 0, "D-FREQ-001": 0, "D-REL-EXTRA-001": 0}

    for record in result["records"]:
        for finding in record["differing_fields"]:
            if finding.get("error_type") != "C":
                continue
            adjudication = _decision(record, finding)
            if adjudication is None:
                raise RuntimeError(f"unclassified residual finding: {record['case_id']} {finding}")
            finding["pre_residual_adjudication_error_type"] = finding["error_type"]
            finding["error_type"] = adjudication["error_type"]
            finding["gold_review_required"] = adjudication["gold_review_required"]
            finding["adjudication"] = adjudication
            applied += 1
            by_decision[adjudication["decision_id"]] += 1
            if adjudication["gold_review_required"]:
                review_queue.append({
                    "case_id": record["case_id"],
                    "surface": record["surface"],
                    "text": record["text"],
                    "segments": record["segments"],
                    "finding": finding,
                })

    type_counts = {"A": 0, "B": 0, "C": 0}
    classification_counts: dict[str, int] = {}
    for record in result["records"]:
        for finding in record["differing_fields"]:
            type_counts[finding["error_type"]] += 1
            classification_counts[finding["classification"]] = classification_counts.get(finding["classification"], 0) + 1

    result["status"] = "residual_type_c_adjudicated"
    result["run_type"] = "v6-residual-type-c-adjudication"
    result["policy_version"] = "1.1"
    result["policy_approver"] = "Carlos Henrique"
    result["gold_modified"] = False
    result["corpus_modified"] = False
    result["resolver_modified"] = False
    result["residual_adjudication"] = {
        "items_considered": 19,
        "items_applied": applied,
        "by_decision": by_decision,
        "type_b_gold_review_queue": len(review_queue),
        "gold_review_queue": review_queue,
    }
    result["summary"] = {
        "records_with_divergence": len(result["records"]),
        "field_and_relation_findings": sum(classification_counts.values()),
        "classification_counts": classification_counts,
        "error_type_counts": type_counts,
        "type_a": type_counts["A"],
        "type_b": type_counts["B"],
        "type_c": type_counts["C"],
        "gold_review_required": len(review_queue),
    }
    result["gold_review_queue"] = review_queue
    result["holdout_evaluation"] = "NOT_EXECUTED"
    result["repair_authorized"] = type_counts["C"] == 0
    result["repair_authorized_scope"] = "TYPE_A_RESOLVER_ERROR only"
    result["next_step"] = "repair-v4-type-a-only" if result["repair_authorized"] else "residual-policy-review"
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
