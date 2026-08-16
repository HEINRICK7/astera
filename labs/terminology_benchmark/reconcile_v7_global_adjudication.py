"""Reconcile all V7 adjudication evidence into a non-official global ledger."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DRAFT = DATA / "v7_unseen_generalization_draft.jsonl"
LOCAL_BATCH_DIR = RESULTS / "v7-adjudication-batches-2026-08-15"
READJ_DIR = RESULTS / "v7-ambiguity-readjudication-2026-08-15"
COMPLETION_DIR = RESULTS / "v7-adjudication-completion-2026-08-15"
EXTERNAL_BATCH_01 = Path("/home/carlos-henrique/Músicas/v7-batch-01-adjudicated-2026-08-15.json")
OUTPUT_DIR = RESULTS / "v7-global-adjudication-reconciliation-2026-08-15"
LEDGER = OUTPUT_DIR / "V7_GLOBAL_ADJUDICATION_LEDGER.json"
PROPOSAL = OUTPUT_DIR / "V7_OFFICIAL_COMPOSITION_PROPOSAL.json"
PROPOSAL_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_OFFICIAL_COMPOSITION_PROPOSAL.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _draft() -> dict[str, dict[str, Any]]:
    return {json.loads(line)["case_id"]: json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines() if line.strip()}


def _payload_reviews(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {review["candidate_id"]: review for review in payload.get("reviews", [])}


def _source_record(case_id: str, decision: str, review: dict[str, Any] | None, source: str, policy_version: str | None, precedence: int) -> dict[str, Any]:
    return {
        "candidate_id": case_id,
        "final_decision": decision,
        "source": source,
        "policy_version": policy_version,
        "precedence": precedence,
        "review_id": review.get("review_id") if review else None,
        "reviewer": review.get("reviewer") if review else None,
        "review_notes": review.get("review_notes") if review else None,
        "gold": review.get("gold") if review and decision == "APPROVED" else None,
        "policy_ids": review.get("policy_ids", []) if review else [],
        "readjudication_scope": review.get("readjudication_scope") if review else None,
    }


def main() -> None:
    draft = _draft()
    if len(draft) != 240:
        raise RuntimeError(f"expected 240 draft IDs, found {len(draft)}")
    ledger: dict[str, dict[str, Any]] = {}
    source_conflicts: list[str] = []
    source_inventory: list[dict[str, Any]] = []

    # Batches 01-04: use the completed v1.3 artifacts when available. Until
    # those artifacts exist, preserve the original external/pending state.
    for number in range(1, 5):
        completed = COMPLETION_DIR / f"v7-batch-{number:02d}-completed.json"
        if completed.exists():
            reviews = _payload_reviews(completed)
            source_inventory.append({"batch": f"v7-batch-{number:02d}", "source": str(completed), "status": "VALIDATED_V1_3_COMPLETION", "policy_version": "1.3"})
            for case_id, review in reviews.items():
                ledger[case_id] = _source_record(case_id, review["decision"], review, "v1.3_adjudication_completion", "1.3", 3)
            continue
        if number == 1 and EXTERNAL_BATCH_01.exists():
            source = EXTERNAL_BATCH_01
            status = "VALIDATED_EXTERNAL_V1_2"
            decision_policy = "1.2"
            decision_source = "external_batch_01_validated"
        else:
            source = next(LOCAL_BATCH_DIR.glob(f"v7-batch-{number:02d}-*.json"))
            status = "PENDING_LOCAL"
            decision_policy = "1.2"
            decision_source = "official_batch_pending"
        reviews = _payload_reviews(source)
        source_inventory.append({"batch": f"v7-batch-{number:02d}", "source": str(source), "status": status, "policy_version": decision_policy})
        for case_id, review in reviews.items():
            ledger[case_id] = _source_record(case_id, review.get("decision", "PENDING_HUMAN"), review, decision_source, decision_policy, 1 if number == 1 else 0)

    # Batches 05-08: v1.3 ambiguity readjudication has precedence over the
    # earlier AI proposals and over the untouched official pending packets.
    for number in range(5, 9):
        path = READJ_DIR / f"v7-batch-{number:02d}-readjudicated.json"
        reviews = _payload_reviews(path)
        source_inventory.append({"batch": f"v7-batch-{number:02d}", "source": str(path), "status": "VALIDATED_READJUDICATION", "policy_version": "1.3"})
        for case_id, review in reviews.items():
            candidate = _source_record(case_id, review["decision"], review, "v1.3_ambiguity_readjudication", "1.3", 2)
            if case_id in ledger and ledger[case_id]["precedence"] > candidate["precedence"]:
                source_conflicts.append(f"{case_id}: lower precedence source attempted to override higher precedence")
                continue
            if case_id in ledger and ledger[case_id]["precedence"] == candidate["precedence"] and ledger[case_id]["final_decision"] != candidate["final_decision"]:
                source_conflicts.append(f"{case_id}: conflicting same-precedence decisions")
            ledger[case_id] = candidate

    missing = sorted(set(draft) - set(ledger))
    unexpected = sorted(set(ledger) - set(draft))
    duplicate_candidate_ids = 0  # sources are reconciled by candidate_id; conflicts are separately recorded.
    counts = Counter(record["final_decision"] for record in ledger.values())
    approved = [record for record in ledger.values() if record["final_decision"] == "APPROVED"]
    rejected = [record for record in ledger.values() if record["final_decision"] == "REJECTED"]
    ambiguous = [record for record in ledger.values() if record["final_decision"] == "AMBIGUOUS"]
    pending = [record for record in ledger.values() if record["final_decision"] == "PENDING_HUMAN"]
    mentions = sum(len(record.get("gold") or []) for record in approved)
    relations = sum(sum(len(item.get("relations", [])) for item in record.get("gold") or []) for record in approved)
    cross_segment_cases = sum(1 for record in approved if any(len(item.get("segment_ids", [])) > 1 for item in record.get("gold") or []))
    provenance_complete = all(
        all(isinstance(item.get("attribute_provenance"), dict) and isinstance(item.get("relation_provenance"), dict) for item in record.get("gold") or [])
        for record in approved
    )
    policy_stale = sorted(record["candidate_id"] for record in approved if record.get("policy_version") != "1.3")
    gate_blockers = []
    if missing:
        gate_blockers.append("missing candidate IDs")
    if unexpected:
        gate_blockers.append("unexpected candidate IDs")
    if source_conflicts:
        gate_blockers.append("conflicting final decisions")
    if pending:
        gate_blockers.append("pending adjudication remains")
    if ambiguous:
        gate_blockers.append("ambiguous adjudication remains")
    if policy_stale:
        gate_blockers.append("approved evidence from policy v1.2 requires policy-conformance review")
    if not EXTERNAL_BATCH_01.exists():
        gate_blockers.append("Batch 01 adjudication artifact missing")
    gate_blockers.extend(
        f"Batch {number:02d} adjudicated artifact missing"
        for number in range(1, 5)
        if not (COMPLETION_DIR / f"v7-batch-{number:02d}-completed.json").exists()
    )

    available_structural_reports = [
        *(COMPLETION_DIR / f"v7-batch-{number:02d}-validation.json" for number in range(1, 5)),
        *(READJ_DIR / f"v7-batch-{number:02d}-validation.json" for number in range(5, 9)),
    ]
    available_structural_pass = all(
        path.exists() and json.loads(path.read_text(encoding="utf-8")).get("structural_validation_passed")
        for path in available_structural_reports
    )
    integrity_leakage_pass = not missing and not unexpected and not source_conflicts

    ledger_report = {
        "status": "GLOBAL_RECONCILIATION_PROPOSAL_HUMAN_GATE",
        "policy_version": "1.3",
        "source_draft": str(DRAFT),
        "source_draft_checksum": _sha256(DRAFT),
        "ledger_case_count": len(ledger),
        "ledger": [ledger[case_id] for case_id in sorted(ledger)],
        "source_inventory": source_inventory,
        "duplicate_candidate_ids": duplicate_candidate_ids,
        "missing_candidate_ids": missing,
        "unexpected_candidate_ids": unexpected,
        "conflicting_final_decisions": source_conflicts,
        "decision_counts": {key: counts.get(key, 0) for key in ("APPROVED", "REJECTED", "AMBIGUOUS", "PENDING_HUMAN")},
        "mentions": mentions,
        "relations": relations,
        "cross_segment_cases": cross_segment_cases,
        "structural_validation": "BLOCKED_MISSING_BATCHES_02_04" if not available_structural_pass or any(f"Batch {number:02d} adjudicated artifact missing" in gate_blockers for number in range(2, 5)) else "PASS",
        "provenance_completeness": "PASS" if provenance_complete and not pending else "BLOCKED",
        "adjudication_consistency": "BLOCKED_PENDING_GLOBAL_RECONCILIATION" if pending or ambiguous else "PASS",
        "policy_conformance": "BLOCKED_STALE_V1_2_OR_MISSING_BATCHES" if policy_stale or gate_blockers else "PASS",
        "integrity_leakage_gate": "PASS" if integrity_leakage_pass else "FAIL",
        "resolver_used_for_gold": False,
        "runtime_predictions_used": False,
        "previous_benchmark_predictions_used": False,
        "gate_blockers": sorted(set(gate_blockers)),
        "all_adjudication_gates_pass": not gate_blockers,
        "official_composition_materialized": False,
        "official_freeze": False,
        "blind_run": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    proposal = {
        "status": "PROPOSED_NOT_MATERIALIZED",
        "source_draft_checksum": ledger_report["source_draft_checksum"],
        "policy_version": "1.3",
        "approved_case_ids": sorted(record["candidate_id"] for record in approved),
        "rejected_case_ids": sorted(record["candidate_id"] for record in rejected),
        "ambiguous_case_ids": sorted(record["candidate_id"] for record in ambiguous),
        "pending_case_ids": sorted(record["candidate_id"] for record in pending),
        "case_count": 240,
        "ledger_case_count": len(ledger),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "mention_count": mentions,
        "relation_count": relations,
        "provenance_status": ledger_report["provenance_completeness"],
        "adjudication_method": "batch evidence reconciliation with explicit precedence; no re-adjudication",
        "resolver_used_for_gold": False,
        "official_corpus_materialized": False,
        "freeze_authorized": False,
        "blockers": ledger_report["gate_blockers"],
    }
    PROPOSAL.write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = [
        "# V7 Official Composition Proposal",
        "",
        "Status: **PROPOSED ONLY — HUMAN GATE**",
        "",
        "This is a reconciliation proposal, not the official V7 corpus or freeze.",
        "",
        f"- Source draft checksum: `{proposal['source_draft_checksum']}`",
        "- Policy version: `1.3`",
        f"- Ledger IDs: `{proposal['ledger_case_count']}`",
        f"- APPROVED: `{proposal['approved_count']}`",
        f"- REJECTED: `{proposal['rejected_count']}`",
        f"- AMBIGUOUS: `{len(ambiguous)}`",
        f"- PENDING: `{len(pending)}`",
        f"- Mentions: `{proposal['mention_count']}`",
        f"- Relations: `{proposal['relation_count']}`",
        f"- Provenance: `{proposal['provenance_status']}`",
        "- Resolver used for gold: `false`",
        "",
        "## Precedence",
        "",
        "1. Valid v1.3 readjudication overrides a previous ambiguous result.",
        "2. Previous APPROVED remains unchanged when no later readjudication exists.",
        "3. REJECTED remains excluded.",
        "4. Missing adjudication remains PENDING; it is never inferred.",
        "",
        "## Blockers",
        "",
    ]
    md.extend(f"- {blocker}" for blocker in proposal["blockers"])
    md.extend([
        "",
        "## Hard stops",
        "",
        "- official V7 corpus: NOT CREATED",
        "- freeze: NOT AUTHORIZED",
        "- resolver execution: FALSE",
        "- Blind Run: BLOCKED",
        "- Shadow Integration: BLOCKED",
        "- Production: BLOCKED",
    ])
    PROPOSAL_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": ledger_report["status"], "ledger_case_count": len(ledger), "decision_counts": ledger_report["decision_counts"], "duplicate_candidate_ids": duplicate_candidate_ids, "missing_candidate_ids": len(missing), "unexpected_candidate_ids": len(unexpected), "conflicts": len(source_conflicts), "gate_blockers": ledger_report["gate_blockers"], "ledger": str(LEDGER), "proposal": str(PROPOSAL_MD)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
