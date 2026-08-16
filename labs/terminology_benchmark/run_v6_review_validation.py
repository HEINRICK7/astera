"""Validate human decisions without creating the official V6 corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import ConversationSegment, GoldMention, GoldRelation
from .review_queue import load_candidate_records
from .simulator import CandidateCase, reviewed_candidate_to_case
from .v6_corpus import validate_v6_draft


ROOT = Path(__file__).parent
DEFAULT_CANDIDATES = ROOT / "results" / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl"
DEFAULT_REVIEW = ROOT / "results" / "v6-human-review-template-2026-08-15.json"


def _gold_from_dict(item: dict[str, Any]) -> GoldMention:
    return GoldMention(
        **{
            **item,
            "relations": tuple(GoldRelation(**relation) for relation in item.get("relations", ())),
            "segment_ids": tuple(item.get("segment_ids", ())),
            "attribute_provenance": {
                key: tuple(value) for key, value in item.get("attribute_provenance", {}).items()
            },
            "relation_provenance": {
                key: tuple(value) for key, value in item.get("relation_provenance", {}).items()
            },
        }
    )


def validate_review(candidates_path: Path, review_path: Path) -> dict[str, Any]:
    candidates = load_candidate_records(candidates_path)
    reviews = json.loads(review_path.read_text(encoding="utf-8"))
    if not isinstance(reviews, list):
        raise ValueError("review worksheet must contain a JSON array")
    by_id = {record.get("candidate_id"): record for record in candidates}
    review_by_id = {record.get("candidate_id"): record for record in reviews}
    if set(by_id) != set(review_by_id):
        raise ValueError("review worksheet must contain exactly one record for every candidate")

    approved_cases = []
    counts = {"APPROVED": 0, "REJECTED": 0, "PENDING_REVIEW": 0}
    for candidate_id, candidate_record in by_id.items():
        review = review_by_id[candidate_id]
        decision = review.get("decision", "PENDING_REVIEW")
        if decision not in counts:
            raise ValueError(f"invalid decision for {candidate_id}: {decision}")
        counts[decision] += 1
        if decision == "PENDING_REVIEW":
            continue
        reviewer = str(review.get("reviewer", "")).strip()
        if not reviewer:
            raise ValueError(f"reviewer is required for {candidate_id}")
        if decision == "REJECTED":
            if not str(review.get("review_notes", "")).strip():
                raise ValueError(f"rejection reason is required for {candidate_id}")
            if review.get("gold"):
                raise ValueError(f"rejected candidate must have empty gold: {candidate_id}")
            continue
        gold_payload = review.get("gold", ())
        if not gold_payload:
            raise ValueError(f"approved candidate requires gold: {candidate_id}")
        candidate = CandidateCase(
            **{
                **candidate_record,
                "segments": tuple(
                    ConversationSegment(**segment)
                    for segment in candidate_record.get("segments", ())
                ),
            }
        )
        gold = tuple(_gold_from_dict(item) for item in gold_payload)
        approved_cases.append(
            reviewed_candidate_to_case(
                candidate,
                gold,
                reviewer=reviewer,
                notes=str(review.get("review_notes", "")),
                segment_id=(
                    str(review["segment_id"])
                    if review.get("segment_id") is not None
                    else None
                ),
            )
        )
    provenance_report = validate_v6_draft(approved_cases) if approved_cases else {
        "cases": 0,
        "mentions": 0,
        "segments": 0,
        "sources": {},
        "official": False,
    }
    return {
        "status": "review-incomplete" if counts["PENDING_REVIEW"] else "review-validated",
        "counts": counts,
        "approved_cases": len(approved_cases),
        "official_corpus_created": False,
        "provenance_validation": provenance_report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW)
    args = parser.parse_args()
    print(json.dumps(validate_review(args.candidates, args.review), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
