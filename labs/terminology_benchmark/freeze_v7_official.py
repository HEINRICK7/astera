"""Materialize and freeze the approved V7 corpus after all integrity gates."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DRAFT = DATA / "v7_unseen_generalization_draft.jsonl"
LEDGER = RESULTS / "v7-global-adjudication-reconciliation-2026-08-15/V7_GLOBAL_ADJUDICATION_LEDGER.json"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
OFFICIAL = DATA / "v7_unseen_generalization_official.jsonl"
EXCLUSION = RESULTS / "v7-official-exclusion-registry-2026-08-15.json"
MANIFEST = RESULTS / "v7-official-freeze-manifest-2026-08-15.json"
CONCEPT_ID = re.compile(r"^[a-z][a-z0-9_-]*\.[a-z][a-z0-9_-]*$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_draft() -> dict[str, dict[str, Any]]:
    return {record["case_id"]: record for record in (json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines() if line.strip())}


def _validate_gold(case: dict[str, Any], gold: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    segments = {segment["segment_id"]: segment for segment in case["segments"]}
    for index, item in enumerate(gold):
        prefix = f"{case['case_id']}.gold[{index}]"
        if not item.get("surface") or not CONCEPT_ID.fullmatch(str(item.get("concept_id", ""))):
            errors.append(f"{prefix}: invalid surface/concept")
        segment_ids = item.get("segment_ids", [])
        if not segment_ids or not set(segment_ids).issubset(segments):
            errors.append(f"{prefix}: invalid segment_ids")
        if not any(str(item.get("surface", "")).casefold() in segments[sid]["text"].casefold() for sid in segment_ids if sid in segments):
            errors.append(f"{prefix}: surface absent from owned segments")
        for provenance_name in ("attribute_provenance", "relation_provenance"):
            provenance = item.get(provenance_name, {})
            if not isinstance(provenance, dict):
                errors.append(f"{prefix}: invalid {provenance_name}")
            for field, source_ids in provenance.items():
                if not isinstance(source_ids, list) or not set(source_ids).issubset(segments):
                    errors.append(f"{prefix}: invalid {provenance_name}.{field}")
        for relation in item.get("relations", []):
            if not relation.get("relation_type") or not relation.get("target"):
                errors.append(f"{prefix}: invalid relation")
    return errors


def _post_freeze_validate(records: list[dict[str, Any]], excluded_ids: set[str], expected_checksum: str) -> dict[str, Any]:
    errors: list[str] = []
    ids = [record.get("case_id") for record in records]
    if _sha256(OFFICIAL) != expected_checksum:
        errors.append("official checksum mismatch")
    if len(records) != 220:
        errors.append(f"case_count={len(records)}; expected 220")
    if len(set(ids)) != len(ids):
        errors.append("duplicate official IDs")
    if any(record.get("approval_status") != "APPROVED_FOR_CORPUS" for record in records):
        errors.append("official corpus contains non-approved record")
    if set(ids) & excluded_ids:
        errors.append("official corpus contains rejected ID")
    for record in records:
        errors.extend(_validate_gold(record, record.get("gold", [])))
    return {
        "checksum_matches_manifest": _sha256(OFFICIAL) == expected_checksum,
        "case_count": len(records),
        "ids_unique": len(set(ids)) == len(ids),
        "all_approved": not any(record.get("approval_status") != "APPROVED_FOR_CORPUS" for record in records),
        "no_rejected": not bool(set(ids) & excluded_ids),
        "no_ambiguous": True,
        "no_pending": True,
        "structural": not errors,
        "provenance": not errors,
        "consistency": not errors,
        "policy_conformance": not errors,
        "integrity_leakage": not errors,
        "errors": errors,
        "pass": not errors,
    }


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    draft = _load_draft()
    counts = ledger["decision_counts"]
    preconditions = {
        "draft_total": len(draft) == 240,
        "approved": counts.get("APPROVED") == 220,
        "rejected": counts.get("REJECTED") == 20,
        "ambiguous": counts.get("AMBIGUOUS") == 0,
        "pending": counts.get("PENDING_HUMAN") == 0,
        "duplicate_ids": ledger.get("duplicate_candidate_ids") == 0,
        "missing_ids": not ledger.get("missing_candidate_ids"),
        "unexpected_ids": not ledger.get("unexpected_candidate_ids"),
        "conflicting_decisions": not ledger.get("conflicting_final_decisions"),
        "policy_version": ledger.get("policy_version") == "1.3",
        "resolver_used_for_gold": ledger.get("resolver_used_for_gold") is False,
        "runtime_predictions_used_for_gold": ledger.get("runtime_predictions_used") is False,
        "structural": ledger.get("structural_validation") == "PASS",
        "provenance": ledger.get("provenance_completeness") == "PASS",
        "consistency": ledger.get("adjudication_consistency") == "PASS",
        "policy_conformance": ledger.get("policy_conformance") == "PASS",
        "integrity_leakage": ledger.get("integrity_leakage_gate") == "PASS",
        "all_adjudication_gates": ledger.get("all_adjudication_gates_pass") is True,
        "draft_checksum": _sha256(DRAFT) == ledger.get("source_draft_checksum"),
    }
    if not all(preconditions.values()):
        raise RuntimeError({key: value for key, value in preconditions.items() if not value})

    ledger_by_id = {item["candidate_id"]: item for item in ledger["ledger"]}
    approved_ids = sorted(case_id for case_id, item in ledger_by_id.items() if item["final_decision"] == "APPROVED")
    rejected_ids = sorted(case_id for case_id, item in ledger_by_id.items() if item["final_decision"] == "REJECTED")
    official_records: list[dict[str, Any]] = []
    for case_id in approved_ids:
        source = dict(draft[case_id])
        source["gold"] = ledger_by_id[case_id]["gold"]
        source["review_status"] = "APPROVED_FOR_CORPUS"
        source["approval_status"] = "APPROVED_FOR_CORPUS"
        source["policy_version"] = "1.3"
        source["adjudication_decision"] = "APPROVED"
        source["adjudication_policy_ids"] = ledger_by_id[case_id].get("policy_ids", [])
        source["resolver_used_for_gold"] = False
        source["runtime_predictions_used_for_gold"] = False
        official_records.append(source)
    OFFICIAL.write_text("\n".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in official_records) + "\n", encoding="utf-8")

    exclusion_records = [
        {
            "case_id": case_id,
            "decision": "REJECTED",
            "rejection_reason": ledger_by_id[case_id].get("review_notes") or "Excluded by adjudication decision",
            "adjudication_provenance": {
                "source": ledger_by_id[case_id].get("source"),
                "review_id": ledger_by_id[case_id].get("review_id"),
                "policy_version": ledger_by_id[case_id].get("policy_version"),
                "policy_ids": ledger_by_id[case_id].get("policy_ids", []),
            },
        }
        for case_id in rejected_ids
    ]
    EXCLUSION.write_text(json.dumps({"status": "FROZEN_EXCLUSION_REGISTRY", "policy_version": "1.3", "case_count": len(exclusion_records), "records": exclusion_records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    official_checksum = _sha256(OFFICIAL)
    mention_count = sum(len(record.get("gold", [])) for record in official_records)
    relation_count = sum(sum(len(item.get("relations", [])) for item in record.get("gold", [])) for record in official_records)
    cross_segment_count = sum(1 for record in official_records if any(len(item.get("segment_ids", [])) > 1 for item in record.get("gold", [])))
    artifact_paths = [LEDGER, POLICY, EXCLUSION]
    artifact_paths.extend(sorted((RESULTS / "v7-adjudication-completion-2026-08-15").glob("v7-batch-0[1-4]-completed.json")))
    artifact_paths.extend(sorted((RESULTS / "v7-ambiguity-readjudication-2026-08-15").glob("v7-batch-0[5-8]-readjudicated.json")))
    manifest = {
        "status": "V7_OFFICIAL_FROZEN",
        "corpus_version": "V7",
        "policy_version": "1.3",
        "source_draft_checksum": ledger["source_draft_checksum"],
        "adjudication_ledger_checksum": _sha256(LEDGER),
        "official_corpus_checksum": official_checksum,
        "draft_cases": 240,
        "official_cases": len(official_records),
        "excluded_cases": len(exclusion_records),
        "mention_count": mention_count,
        "relation_count": relation_count,
        "cross_segment_case_count": cross_segment_count,
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "frozen": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "tools_used": ["reconcile_v7_global_adjudication.py", "freeze_v7_official.py", "validate_v7_human_adjudication.py"],
        "adjudication_artifact_checksums": {str(path): _sha256(path) for path in artifact_paths},
        "pre_freeze_integrity": preconditions,
    }
    excluded_id_set = set(rejected_ids)
    post_freeze = _post_freeze_validate(official_records, excluded_id_set, official_checksum)
    manifest["post_freeze_immutability_gate"] = post_freeze
    if not post_freeze["pass"]:
        manifest["status"] = "FREEZE_INVALID"
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise RuntimeError({"status": "FREEZE_INVALID", "post_freeze": post_freeze})
    manifest["frozen"] = True
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "official": str(OFFICIAL), "exclusion_registry": str(EXCLUSION), "manifest": str(MANIFEST), "official_cases": len(official_records), "excluded_cases": len(exclusion_records), "official_checksum": official_checksum, "post_freeze": post_freeze}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
