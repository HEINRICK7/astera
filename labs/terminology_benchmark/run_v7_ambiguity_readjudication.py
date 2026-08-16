"""Readjudicate only the 50 V7 ambiguity proposals under policy v1.3.

The existing 70 APPROVED proposals are copied unchanged for audit context. The
resolver is never imported or executed, and the official V7 queue remains
untouched.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_v7_ai_assisted_adjudication import (
    _first_id,
    _medication,
    _segments,
    _symptom,
    _variant,
)


ROOT = Path(__file__).parent
PROPOSAL_DIR = ROOT / "results/v7-ai-assisted-adjudication-2026-08-15"
OUTPUT_DIR = ROOT / "results/v7-ambiguity-readjudication-2026-08-15"
POLICY = "clinical-semantic-policy-v1.3"
AI_REVIEWER = "NIEDE AI-assisted semantic governance — policy v1.3 readjudication"
TARGET_CLUSTERS = {"AMB-FREQ-001", "AMB-TEMP-001", "AMB-CORR-001", "AMB-SELF-001", "AMB-SPEAKER-001"}


def _readjudicated_gold(review: dict[str, Any]) -> tuple[str, list[dict[str, Any]] | None, str, list[str]]:
    cluster = review["ambiguity_cluster"]
    segments = _segments(review)
    med_a, med_b, symptom, _location, _old_dose, new_dose, frequency, temporal, _relative = _variant(review["candidate_id"])
    if cluster == "AMB-FREQ-001":
        gold = [_medication(
            review, med_b, frequency=frequency,
            concept_segment=_first_id(segments, med_b, 1),
            attribute_segment=_first_id(segments, frequency, 4),
            status="active",
        )]
        return "APPROVED", gold, "SEM-FREQ-002: explicit current frequency retained; no CHANGED_FROM because old/new values are not distinct.", ["SEM-FREQ-001", "SEM-FREQ-002"]
    if cluster == "AMB-TEMP-001":
        gold = [_symptom(
            review, symptom, temporality="past",
            concept_segment=_first_id(segments, symptom, 1),
            attribute_segment=_first_id(segments, temporal, 2),
            segment_ids=list(dict.fromkeys([_first_id(segments, symptom, 1), _first_id(segments, temporal, 2)])),
        )]
        return "APPROVED", gold, "SEM-TEMP-001 + SEM-XSEG-001: named past event is retained; generic current phrase does not inherit an unresolved concept.", ["SEM-TEMP-001", "SEM-XSEG-001"]
    if cluster == "AMB-CORR-001":
        return "REJECTED", None, "SEM-CORR-001: explicit correction supersedes the rejected clinical term; location-only residue is not a clinical entity.", ["SEM-CORR-001"]
    if cluster == "AMB-SELF-001":
        gold = [_medication(
            review, med_a, dose=new_dose,
            concept_segment=_first_id(segments, med_a, 1),
            attribute_segment=_first_id(segments, new_dose, 4),
            status="active",
        )]
        return "APPROVED", gold, "SEM-SELF-001: later self-corrected dose owns the current attribute; no CHANGED_FROM is created from the correction.", ["SEM-DOSE-001", "SEM-SELF-001"]
    if cluster == "AMB-SPEAKER-001":
        medication = _medication(
            review, med_b, frequency=frequency,
            concept_segment=_first_id(segments, med_b, 4),
            attribute_segment=_first_id(segments, frequency, 4),
            status="active",
        )
        patient_symptom = _symptom(
            review, symptom, negated=True, temporality="current",
            concept_segment=_first_id(segments, symptom, 1),
            attribute_segment=_first_id(segments, symptom, 4),
            segment_ids=list(dict.fromkeys([_first_id(segments, symptom, 1), _first_id(segments, symptom, 4)])),
        )
        return "APPROVED", [medication, patient_symptom], "SEM-EXP-001 + SEM-XSEG-001: speaker is not experiencer; ambiguous prior ownership remains unresolved while explicit patient mentions are retained.", ["SEM-EXP-001", "SEM-XSEG-001"]
    raise ValueError(f"unsupported ambiguity cluster: {cluster}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    batch_summaries = []
    for batch_number in range(5, 9):
        path = next(PROPOSAL_DIR.glob(f"v7-batch-{batch_number:02d}-ai-proposal.json"))
        payload = json.loads(path.read_text(encoding="utf-8"))
        output_reviews: list[dict[str, Any]] = []
        changed_ids: list[str] = []
        for original in payload["reviews"]:
            review = dict(original)
            cluster = review.get("ambiguity_cluster")
            if original.get("decision") == "AMBIGUOUS":
                if cluster not in TARGET_CLUSTERS:
                    raise RuntimeError(f"unexpected ambiguity cluster {cluster}")
                decision, gold, note, policies = _readjudicated_gold(original)
                review.update({
                    "decision": decision,
                    "reviewer": AI_REVIEWER,
                    "policy_version": POLICY,
                    "review_notes": note,
                    "gold": gold,
                    "policy_ids": policies,
                    "ambiguity_cluster": None,
                    "readjudication_source_cluster": cluster,
                    "readjudication_scope": "AMBIGUOUS_ONLY",
                })
                changed_ids.append(original["candidate_id"])
            else:
                # Preserve previously approved content byte-for-byte at the
                # semantic level; only annotate its audit scope.
                review["readjudication_scope"] = "NOT_REPROCESSED_APPROVED_CARRIED_FORWARD"
            output_reviews.append(review)
        counts = {key: sum(item.get("decision") == key for item in output_reviews) for key in ("APPROVED", "REJECTED", "AMBIGUOUS", "PENDING_HUMAN")}
        output = OUTPUT_DIR / f"v7-batch-{batch_number:02d}-readjudicated.json"
        output.write_text(json.dumps({
            "status": "V7_AMBIGUITY_READJUDICATION_PENDING_AUDIT",
            "batch_id": payload["batch_id"],
            "case_range": payload["case_range"],
            "policy_version": POLICY,
            "source_proposal": str(path),
            "readjudication_scope": "AMBIGUOUS_ONLY",
            "approved_cases_reprocessed": False,
            "gold_generation": "POLICY_BOUND_READJUDICATION_NOT_OFFICIAL_COMPOSITION",
            "resolver_execution": False,
            "runtime_predictions_used": False,
            "previous_benchmark_predictions_used": False,
            "decision_counts": counts,
            "changed_case_ids": changed_ids,
            "reviews": output_reviews,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        batch_summaries.append({"batch_id": payload["batch_id"], "case_range": payload["case_range"], "decision_counts": counts, "changed_cases": len(changed_ids), "output": str(output)})
    print(json.dumps({"status": "V7_AMBIGUITY_READJUDICATION_READY_FOR_AUDIT", "policy_version": "1.3", "batches": batch_summaries, "resolver_execution": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
