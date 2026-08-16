"""Audit the policy-bound V7 ambiguity readjudication without freezing V7."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from consolidate_v7_ai_assisted_adjudication import _normalized_shape


ROOT = Path(__file__).parent
PROPOSAL_DIR = ROOT / "results/v7-ai-assisted-adjudication-2026-08-15"
READJ_DIR = ROOT / "results/v7-ambiguity-readjudication-2026-08-15"
OUTPUT = READJ_DIR / "V7_AMBIGUITY_READJUDICATION_AUDIT.json"
OUTPUT_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_AMBIGUITY_READJUDICATION_AUDIT.md"
TARGET_CLUSTERS = {"AMB-FREQ-001", "AMB-TEMP-001", "AMB-CORR-001", "AMB-SELF-001", "AMB-SPEAKER-001"}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relation_types(review: dict[str, Any]) -> list[str]:
    return [relation.get("relation_type") for item in (review.get("gold") or []) for relation in item.get("relations", [])]


def main() -> None:
    readjudicated = []
    structural_reports = []
    for number in range(5, 9):
        readjudicated.append(_load(READJ_DIR / f"v7-batch-{number:02d}-readjudicated.json"))
        structural_reports.append(_load(READJ_DIR / f"v7-batch-{number:02d}-validation.json"))

    reviews = [review for payload in readjudicated for review in payload["reviews"]]
    source_reviews = {
        review["candidate_id"]: review
        for payload in (_load(PROPOSAL_DIR / f"v7-batch-{number:02d}-ai-proposal.json") for number in range(5, 9))
        for review in payload["reviews"]
    }
    changed = [review for review in reviews if review.get("readjudication_scope") == "AMBIGUOUS_ONLY"]
    changed_ids = {review["candidate_id"] for review in changed}
    source_ambiguous_ids = {review["candidate_id"] for review in source_reviews.values() if review.get("decision") == "AMBIGUOUS"}
    approved_carry_forward_ok = all(
        review.get("decision") != "APPROVED"
        or review.get("readjudication_scope") != "NOT_REPROCESSED_APPROVED_CARRIED_FORWARD"
        or review.get("gold") == source_reviews[review["candidate_id"]].get("gold")
        for review in reviews
    )

    policy_conformance: list[str] = []
    cluster_results: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    family_decisions: defaultdict[str, set[str]] = defaultdict(set)
    family_shapes: defaultdict[str, set[tuple[Any, ...]]] = defaultdict(set)
    for review in changed:
        cluster = review.get("readjudication_source_cluster")
        cluster_results[cluster].append(review)
        relation_types = _relation_types(review)
        if cluster == "AMB-FREQ-001":
            if review.get("decision") != "APPROVED" or "CHANGED_FROM" in relation_types or "HAS_FREQUENCY" not in relation_types:
                policy_conformance.append(f"{review['candidate_id']}: SEM-FREQ-002 violation")
        elif cluster == "AMB-TEMP-001":
            gold = review.get("gold") or []
            if review.get("decision") != "APPROVED" or len(gold) != 1 or gold[0].get("temporality") != "past":
                policy_conformance.append(f"{review['candidate_id']}: SEM-TEMP-001/XSEG conformance failure")
        elif cluster == "AMB-CORR-001":
            if review.get("decision") != "REJECTED" or review.get("gold") is not None:
                policy_conformance.append(f"{review['candidate_id']}: SEM-CORR-001 violation")
        elif cluster == "AMB-SELF-001":
            if review.get("decision") != "APPROVED" or "CHANGED_FROM" in relation_types:
                policy_conformance.append(f"{review['candidate_id']}: SEM-SELF-001 violation")
        elif cluster == "AMB-SPEAKER-001":
            if review.get("decision") != "APPROVED" or any(item.get("experiencer") == "family" for item in review.get("gold", [])):
                policy_conformance.append(f"{review['candidate_id']}: SEM-EXP/XSEG conformance failure")

    for review in reviews:
        family = str(review.get("scenario_family"))
        family_decisions[family].add(str(review.get("decision")))
        if review.get("decision") == "APPROVED":
            family_shapes[family].add(_normalized_shape(review.get("gold") or []))
    consistency_errors = []
    for family, decisions in sorted(family_decisions.items()):
        if len(decisions) > 1:
            consistency_errors.append(f"{family}: mixed decisions {sorted(decisions)}")
        if len(family_shapes.get(family, set())) > 1:
            consistency_errors.append(f"{family}: approved semantic shape diverges")

    structural_pass = all(report.get("structural_validation_passed") for report in structural_reports)
    provenance_complete = all(report.get("provenance_valid") == report.get("provenance_valid_total_approved") for report in structural_reports)
    counts = Counter(review.get("decision") for review in reviews)
    integrity = {
        "changed_case_count": len(changed),
        "source_ambiguous_count": len(source_ambiguous_ids),
        "changed_ids_match_source_ambiguous": changed_ids == source_ambiguous_ids,
        "approved_carry_forward_unchanged": approved_carry_forward_ok,
        "resolver_execution": all(not payload.get("resolver_execution") for payload in readjudicated),
        "runtime_predictions_used": all(not payload.get("runtime_predictions_used") for payload in readjudicated),
        "previous_benchmark_predictions_used": all(not payload.get("previous_benchmark_predictions_used") for payload in readjudicated),
        "official_composition_materialized": False,
        "corpus_freeze_complete": False,
    }

    proposed_composition = {
        "status": "PROPOSED_NOT_MATERIALIZED",
        "policy_version": "1.3",
        "scope": "V7 cases 121-240 readjudication audit",
        "include_decisions": ["APPROVED"],
        "exclude_decisions": ["REJECTED"],
        "case_count_in_scope": len(reviews),
        "approved_in_scope": counts.get("APPROVED", 0),
        "rejected_in_scope": counts.get("REJECTED", 0),
        "pending_or_ambiguous_in_scope": counts.get("PENDING_HUMAN", 0) + counts.get("AMBIGUOUS", 0),
        "official_240_case_manifest_ready": False,
        "manifest_blockers": [
            "official composition not authorized",
            "batches 01-04 are not materialized in this readjudication artifact",
        ],
        "manifest_rule": "include only cases with final APPROVED adjudication; exclude REJECTED; preserve source/provenance and policy version",
    }
    report = {
        "status": "V7_COMPOSITION_AUTHORIZATION_GATE",
        "policy_version": "1.3",
        "scope": "AMBIGUOUS_ONLY_BATCHES_05_08",
        "total_cases_in_audited_scope": len(reviews),
        "decision_counts": {key: counts.get(key, 0) for key in ("APPROVED", "AMBIGUOUS", "REJECTED", "PENDING_HUMAN")},
        "mentions": sum(report.get("mentions", 0) for report in structural_reports),
        "relations": sum(report.get("relations", 0) for report in structural_reports),
        "provenance_completeness": "PASS" if provenance_complete else "FAIL",
        "adjudication_consistency": "PASS" if not consistency_errors else "FAIL",
        "adjudication_consistency_errors": consistency_errors,
        "policy_conformance": "PASS" if not policy_conformance else "FAIL",
        "policy_conformance_errors": policy_conformance,
        "structural_validation": "PASS" if structural_pass else "FAIL",
        "structural_errors": [error for report in structural_reports for error in report.get("structural_errors", [])],
        "cluster_remaining": {cluster: sum(item.get("decision") == "AMBIGUOUS" for item in items) for cluster, items in sorted(cluster_results.items())},
        "cluster_final_counts": {cluster: dict(Counter(item.get("decision") for item in items)) for cluster, items in sorted(cluster_results.items())},
        "integrity_leakage_gate": "PASS" if all(
            integrity[key] for key in (
                "changed_ids_match_source_ambiguous",
                "approved_carry_forward_unchanged",
                "resolver_execution",
                "runtime_predictions_used",
                "previous_benchmark_predictions_used",
            )
        ) else "FAIL",
        "integrity_details": integrity,
        "proposed_composition_and_manifest": proposed_composition,
        "blind_run": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
        "next_action": "HUMAN_GATE_COMPOSITION_AUTHORIZATION",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# V7 Ambiguity Readjudication Audit",
        "",
        "Status: **V7 COMPOSITION AUTHORIZATION GATE**",
        "",
        "No official V7 composition or freeze was performed.",
        "",
        f"- Policy: `v{report['policy_version']}`",
        f"- Audited cases: `{report['total_cases_in_audited_scope']}`",
        f"- APPROVED: `{report['decision_counts']['APPROVED']}`",
        f"- REJECTED: `{report['decision_counts']['REJECTED']}`",
        f"- AMBIGUOUS: `{report['decision_counts']['AMBIGUOUS']}`",
        f"- PENDING_HUMAN: `{report['decision_counts']['PENDING_HUMAN']}`",
        f"- Structural validation: `{report['structural_validation']}`",
        f"- Provenance completeness: `{report['provenance_completeness']}`",
        f"- Adjudication consistency: `{report['adjudication_consistency']}`",
        f"- Policy conformance: `{report['policy_conformance']}`",
        f"- Leakage/integrity gate: `{report['integrity_leakage_gate']}`",
        "",
        "## Remaining ambiguity by cluster",
        "",
    ]
    for cluster, remaining in report["cluster_remaining"].items():
        lines.append(f"- `{cluster}`: `{remaining}`")
    lines.extend([
        "",
        "## Proposed composition",
        "",
        "The exact composition rule is recorded in the JSON report but is not materialized: include only final APPROVED cases, exclude REJECTED cases, preserve source/provenance, and keep policy version v1.3.",
        "",
        "## Hard stops",
        "",
        "- official V7 corpus: NOT CREATED",
        "- manifest: PROPOSED ONLY",
        "- resolver execution: FALSE",
        "- Blind Run: BLOCKED",
        "- Shadow Integration: BLOCKED",
        "- Production: BLOCKED",
    ])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "decision_counts": report["decision_counts"], "structural_validation": report["structural_validation"], "provenance": report["provenance_completeness"], "policy_conformance": report["policy_conformance"], "integrity": report["integrity_leakage_gate"], "output": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
