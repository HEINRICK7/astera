"""Complete V7 adjudication for batches 01-04 under policy v1.3.

This produces non-official adjudication artifacts only. It never executes or
imports the resolver and never mutates the V7 draft or official queue.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_v7_ai_assisted_adjudication import _build_gold, _proposal
from run_v7_ambiguity_readjudication import _readjudicated_gold


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
LOCAL_BATCH_DIR = RESULTS / "v7-adjudication-batches-2026-08-15"
OUT_DIR = RESULTS / "v7-adjudication-completion-2026-08-15"
EXTERNAL_BATCH_01 = Path("/home/carlos-henrique/Músicas/v7-batch-01-adjudicated-2026-08-15.json")
POLICY = "clinical-semantic-policy-v1.3"
REVIEWER = "NIEDE AI-assisted semantic governance — v1.3 completion"
CLUSTER_BY_FAMILY = {
    "FREQUENCY_STATUS_TRANSITION": "AMB-FREQ-001",
    "DISTRIBUTED_TEMPORALITY": "AMB-TEMP-001",
    "CLINICIAN_CORRECTION": "AMB-CORR-001",
    "PATIENT_SELF_CORRECTION": "AMB-SELF-001",
    "ANAPHORA_SPEAKER_TRANSITION": "AMB-SPEAKER-001",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _finalize_review(review: dict[str, Any]) -> dict[str, Any]:
    family = review["scenario_family"]
    if family in CLUSTER_BY_FAMILY:
        working = dict(review)
        working["ambiguity_cluster"] = CLUSTER_BY_FAMILY[family]
        decision, gold, note, policies = _readjudicated_gold(working)
        return {
            **review,
            "decision": decision,
            "reviewer": REVIEWER,
            "policy_version": POLICY,
            "effective_policy_version": POLICY,
            "review_notes": note,
            "gold": gold,
            "policy_ids": policies,
            "readjudication_source_cluster": CLUSTER_BY_FAMILY[family],
            "readjudication_scope": "AMBIGUOUS_ONLY" if review.get("decision") == "AMBIGUOUS" else "NEW_CASE_ADJUDICATION",
            "gold_generation": "POLICY_BOUND_ADJUDICATION_NOT_OFFICIAL_COMPOSITION",
        }
    gold = _build_gold(review)
    return {
        **review,
        "decision": "APPROVED",
        "reviewer": REVIEWER,
        "policy_version": POLICY,
        "effective_policy_version": POLICY,
        "review_notes": "Policy-bound adjudication under v1.3; no resolver evidence used.",
        "gold": gold,
        "policy_ids": ["SEM-STATUS-001", "SEM-XSEG-001"],
        "readjudication_scope": "NEW_CASE_ADJUDICATION",
        "gold_generation": "POLICY_BOUND_ADJUDICATION_NOT_OFFICIAL_COMPOSITION",
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []

    # Batch 01: carry approved reviews unchanged; resolve only its 11 old
    # ambiguous cases with the current policy.
    if not EXTERNAL_BATCH_01.exists():
        raise RuntimeError(f"missing validated Batch 01 artifact: {EXTERNAL_BATCH_01}")
    batch_sources: dict[int, tuple[Path, str]] = {1: (EXTERNAL_BATCH_01, "EXTERNAL_VALIDATED_V1_2")}
    for number in range(2, 5):
        path = next(LOCAL_BATCH_DIR.glob(f"v7-batch-{number:02d}-*.json"))
        batch_sources[number] = (path, "PENDING_LOCAL_ADJUDICATION")

    for number, (source, source_status) in batch_sources.items():
        payload = _load(source)
        reviews = payload.get("reviews", [])
        output_reviews: list[dict[str, Any]] = []
        changed_ids: list[str] = []
        for original in reviews:
            if number == 1 and original.get("decision") == "APPROVED":
                # No semantic reprocessing of the 19 existing approved cases.
                output_reviews.append({
                    **original,
                    "effective_policy_version": POLICY,
                    "readjudication_scope": "NOT_REPROCESSED_APPROVED_CARRIED_FORWARD",
                    "gold_generation": "HUMAN_APPROVED_CARRIED_FORWARD",
                })
                continue
            finalized = _finalize_review(original)
            output_reviews.append(finalized)
            if original.get("decision") == "AMBIGUOUS":
                changed_ids.append(original["candidate_id"])
        counts = {key: sum(item.get("decision") == key for item in output_reviews) for key in ("APPROVED", "REJECTED", "AMBIGUOUS", "PENDING_HUMAN")}
        output = OUT_DIR / f"v7-batch-{number:02d}-completed.json"
        output.write_text(json.dumps({
            "status": "V7_ADJUDICATION_COMPLETION_PENDING_GLOBAL_AUDIT",
            "batch_id": payload.get("batch_id", f"v7-batch-{number:02d}"),
            "case_range": payload.get("case_range"),
            "policy_version": POLICY,
            "source_artifact": str(source),
            "source_status": source_status,
            "readjudication_scope": "BATCH_01_AMBIGUOUS_ONLY" if number == 1 else "BATCH_FULL_PENDING_CASES",
            "approved_cases_reprocessed": False,
            "gold_generation": "POLICY_BOUND_ADJUDICATION_NOT_OFFICIAL_COMPOSITION",
            "resolver_execution": False,
            "runtime_predictions_used": False,
            "previous_benchmark_predictions_used": False,
            "decision_counts": counts,
            "changed_case_ids": changed_ids,
            "reviews": output_reviews,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summaries.append({"batch_id": f"v7-batch-{number:02d}", "case_range": payload.get("case_range"), "decision_counts": counts, "changed_cases": len(changed_ids), "output": str(output)})
    print(json.dumps({"status": "V7_ADJUDICATION_COMPLETION_READY_FOR_AUDIT", "policy_version": "1.3", "batches": summaries, "resolver_execution": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
