"""Prepare human-only V7 gold-adjudication batches.

This tool copies draft cases into editable review packets but never fills gold,
chooses a decision, or calls the resolver.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DRAFT = DATA / "v7_unseen_generalization_draft.jsonl"
BATCH_DIR = RESULTS / "v7-adjudication-batches-2026-08-15"
MANIFEST = RESULTS / "v7-adjudication-manifest-2026-08-15.json"
BATCH_SIZE = 30
POLICY = "clinical-semantic-policy-v1.2"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_draft() -> list[dict[str, Any]]:
    return [json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines() if line.strip()]


def _review_form(record: dict[str, Any], review_index: int) -> dict[str, Any]:
    return {
        "review_id": f"v7-review-{review_index:04d}",
        "candidate_id": record["case_id"],
        "text": record["text"],
        "segments": record["segments"],
        "scenario_family": record["scenario_family"],
        "decision": "PENDING_HUMAN",
        "reviewer": None,
        "review_notes": None,
        "policy_version": POLICY,
        "semantic_equivalence_group": None,
        "gold": None,
        "adjudication_form": {
            "mentions": None,
            "concept_id": None,
            "negation": None,
            "certainty": None,
            "temporality": None,
            "experiencer": None,
            "laterality": None,
            "dose": None,
            "dose_unit": None,
            "frequency": None,
            "status": None,
            "relations": None,
            "speaker": None,
            "segment_ownership": None,
            "attribute_provenance": None,
            "relation_provenance": None,
        },
        "structural_review": {
            "surface_exists_in_segment": None,
            "concept_id_valid": None,
            "segment_ids_exist": None,
            "provenance_segments_exist": None,
            "relation_endpoints_exist": None,
            "attributes_schema_valid": None,
        },
        "mention_candidates": record.get("mention_candidates", []),
        "review_dimensions": record.get("review_dimensions", []),
        "decision_rule": "APPROVED requires explicit human gold; REJECTED/AMBIGUOUS do not create gold; PENDING remains blocked",
    }


def main() -> None:
    records = _load_draft()
    if len(records) != 240:
        raise RuntimeError(f"V7 draft must contain 240 cases, found {len(records)}")
    if any(record.get("gold") is not None or record.get("review_status") != "PENDING_HUMAN" for record in records):
        raise RuntimeError("draft changed before adjudication: expected gold=null and PENDING_HUMAN")
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    batch_paths: list[str] = []
    for batch_number, start in enumerate(range(0, len(records), BATCH_SIZE), start=1):
        batch_records = records[start : start + BATCH_SIZE]
        reviews = [_review_form(record, start + offset + 1) for offset, record in enumerate(batch_records)]
        batch = {
            "status": "HUMAN_REVIEW_REQUIRED",
            "batch_id": f"v7-batch-{batch_number:02d}",
            "case_range": f"{start + 1:03d}-{start + len(batch_records):03d}",
            "policy_version": POLICY,
            "source_draft": str(DRAFT),
            "gold_generation": "FORBIDDEN",
            "decision_counts": {"APPROVED": 0, "REJECTED": 0, "AMBIGUOUS": 0, "PENDING_HUMAN": len(reviews)},
            "reviews": reviews,
        }
        path = BATCH_DIR / f"v7-batch-{batch_number:02d}-cases-{start + 1:03d}-{start + len(batch_records):03d}.json"
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        batch_paths.append(str(path))
    manifest = {
        "status": "HUMAN_ADJUDICATION_IN_PROGRESS",
        "corpus": "V7 Unseen Generalization",
        "policy_version": POLICY,
        "source_draft": str(DRAFT),
        "source_draft_sha256": _sha256(DRAFT),
        "batch_count": len(batch_paths),
        "batch_size": BATCH_SIZE,
        "case_count": len(records),
        "case_ranges": [f"{start + 1:03d}-{start + BATCH_SIZE:03d}" for start in range(0, len(records), BATCH_SIZE)],
        "batch_paths": batch_paths,
        "decision_counts": {"APPROVED": 0, "REJECTED": 0, "AMBIGUOUS": 0, "PENDING_HUMAN": len(records)},
        "mentions": 0,
        "relations": 0,
        "cross_segment_cases": None,
        "provenance_valid": None,
        "adjudication_consistency": "NOT_COMPUTABLE_PENDING_HUMAN",
        "human_review_complete": False,
        "gold_validation_complete": False,
        "corpus_freeze_complete": False,
        "official_v7_run": False,
        "resolver_executed": False,
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "batch_count": len(batch_paths), "case_count": len(records), "manifest": str(MANIFEST)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
