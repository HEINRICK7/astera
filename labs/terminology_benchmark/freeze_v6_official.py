"""Freeze the pre-registered V6 corpus after deterministic human review."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from .corpus import (
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    CONTEXT_VALIDATION_V6_DRAFT_PATH,
    CONTEXT_VALIDATION_V6_PATH,
    load_corpus,
)
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation
from .review_queue import load_candidate_records
from .simulator import CandidateCase, reviewed_candidate_to_case
from .v6_corpus import V6AssemblyBlocked, assert_official_v6_ready, validate_v6_draft


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
DEFAULT_MANIFEST = RESULTS / "v6-official-freeze-manifest-2026-08-15.json"
SELECTION_POLICY = (
    "first approved candidates by stable candidate_id order until the "
    "pre-registered quota of 45 is reached"
)
RESERVE_IDS = ("sim-v6-0056", "sim-v6-0057", "sim-v6-0058")

REVIEW_INPUTS = (
    (
        RESULTS / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl",
        RESULTS / "v6-human-review-submission-2026-08-15.json",
    ),
    (
        RESULTS / "clinical-language-simulator-v6-expansion-2026-08-15.jsonl",
        RESULTS / "v6-human-review-expansion-submission-2026-08-15.json",
    ),
    (
        RESULTS / "clinical-language-simulator-v6-micro-expansion-2026-08-15.jsonl",
        RESULTS / "v6-human-review-micro-expansion-submission-2026-08-15.json",
    ),
)


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


def _reviewed_cases(candidates_path: Path, review_path: Path) -> tuple[dict[str, int], tuple[BenchmarkCase, ...]]:
    candidates = load_candidate_records(candidates_path)
    reviews = json.loads(review_path.read_text(encoding="utf-8"))
    if not isinstance(reviews, list):
        raise V6AssemblyBlocked(f"review worksheet must be a JSON array: {review_path}")
    by_id = {record.get("candidate_id"): record for record in candidates}
    review_by_id = {record.get("candidate_id"): record for record in reviews}
    if set(by_id) != set(review_by_id):
        raise V6AssemblyBlocked(f"review worksheet IDs do not match candidates: {review_path}")

    counts = {"APPROVED": 0, "REJECTED": 0, "PENDING_REVIEW": 0}
    approved: list[BenchmarkCase] = []
    for candidate_id in sorted(by_id):
        candidate_record = by_id[candidate_id]
        review = review_by_id[candidate_id]
        decision = review.get("decision", "PENDING_REVIEW")
        if decision not in counts:
            raise V6AssemblyBlocked(f"invalid decision for {candidate_id}: {decision}")
        counts[decision] += 1
        if decision == "PENDING_REVIEW":
            continue
        reviewer = str(review.get("reviewer", "")).strip()
        if not reviewer:
            raise V6AssemblyBlocked(f"reviewer is required for {candidate_id}")
        if decision == "REJECTED":
            if not str(review.get("review_notes", "")).strip():
                raise V6AssemblyBlocked(f"rejection reason is required for {candidate_id}")
            if review.get("gold"):
                raise V6AssemblyBlocked(f"rejected candidate has gold: {candidate_id}")
            continue
        gold_payload = review.get("gold", ())
        if not gold_payload:
            raise V6AssemblyBlocked(f"approved candidate has empty gold: {candidate_id}")
        candidate = CandidateCase(
            **{
                **candidate_record,
                "segments": tuple(
                    ConversationSegment(**segment)
                    for segment in candidate_record.get("segments", ())
                ),
            }
        )
        approved.append(
            reviewed_candidate_to_case(
                candidate,
                tuple(_gold_from_dict(item) for item in gold_payload),
                reviewer=reviewer,
                notes=str(review.get("review_notes", "")),
                segment_id=(str(review["segment_id"]) if review.get("segment_id") is not None else None),
            )
        )
    return counts, tuple(approved)


def _gold_to_dict(gold: GoldMention) -> dict[str, object]:
    payload: dict[str, object] = {
        "surface": gold.surface,
        "concept_id": gold.concept_id,
        "negated": gold.negated,
        "certainty": gold.certainty,
        "temporality": gold.temporality,
        "experiencer": gold.experiencer,
        "laterality": gold.laterality,
        "dose": gold.dose,
        "dose_value": gold.dose_value,
        "dose_unit": gold.dose_unit,
        "frequency": gold.frequency,
        "route": gold.route,
        "status": gold.status,
        "occurrence": gold.occurrence,
        "relations": [
            {"relation_type": relation.relation_type, "target": relation.target, "value": relation.value}
            for relation in gold.relations
        ],
        "segment_ids": list(gold.segment_ids),
        "attribute_provenance": {
            key: list(value) for key, value in gold.attribute_provenance.items()
        },
        "relation_provenance": {
            key: list(value) for key, value in gold.relation_provenance.items()
        },
    }
    return payload


def _case_to_dict(case: BenchmarkCase) -> dict[str, object]:
    payload: dict[str, object] = {
        "case_id": case.case_id,
        "language": case.language,
        "text": case.text,
        "source": case.source,
        "gold": [_gold_to_dict(gold) for gold in case.gold],
    }
    if case.segments:
        payload["segments"] = [
            {"segment_id": segment.segment_id, "speaker": segment.speaker, "text": segment.text}
            for segment in case.segments
        ]
    return payload


def _jsonl_bytes(cases: Iterable[BenchmarkCase]) -> bytes:
    return "".join(
        json.dumps(_case_to_dict(case), ensure_ascii=False, separators=(",", ":")) + "\n"
        for case in cases
    ).encode("utf-8")


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def freeze(*, output: Path = CONTEXT_VALIDATION_V6_PATH, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, object]:
    if output.exists():
        raise V6AssemblyBlocked(f"official V6 corpus already exists; refusing to overwrite: {output}")
    all_approved: list[BenchmarkCase] = []
    review_reports: list[dict[str, object]] = []
    for candidates_path, review_path in REVIEW_INPUTS:
        counts, approved = _reviewed_cases(candidates_path, review_path)
        if counts["PENDING_REVIEW"]:
            raise V6AssemblyBlocked(f"review is not closed: {review_path}")
        all_approved.extend(approved)
        review_reports.append({
            "candidates": str(candidates_path),
            "review": str(review_path),
            "counts": counts,
            "approved_cases": len(approved),
        })

    if len(all_approved) != 48:
        raise V6AssemblyBlocked(f"expected 48 approved cases before selection, got {len(all_approved)}")
    approved_ids = [case.case_id for case in all_approved]
    if len(set(approved_ids)) != len(approved_ids):
        raise V6AssemblyBlocked("duplicate approved candidate_id across review rounds")
    validate_v6_draft(tuple(all_approved))

    ordered = tuple(sorted(all_approved, key=lambda case: case.case_id))
    selected = ordered[:45]
    reserve = ordered[45:]
    if tuple(case.case_id for case in reserve) != RESERVE_IDS:
        raise V6AssemblyBlocked(
            f"stable selection produced unexpected reserve: {[case.case_id for case in reserve]}"
        )
    if selected[-1].case_id != "sim-v6-0055":
        raise V6AssemblyBlocked("sim-v6-0055 was not the final selected approved candidate")
    if len(selected) != 45 or any(case.source != "simulator-approved" for case in selected):
        raise V6AssemblyBlocked("official simulator quota is not exactly 45 approved cases")

    draft = load_corpus(CONTEXT_VALIDATION_V6_DRAFT_PATH)
    forbidden = {
        case.text
        for path in (CONTEXT_VALIDATION_V3_PATH, CONTEXT_VALIDATION_V4_PATH, CONTEXT_VALIDATION_V5_PATH)
        for case in load_corpus(path)
    }
    readiness = assert_official_v6_ready(draft, selected, forbidden_texts=forbidden)
    official_cases = tuple(draft) + selected
    content = _jsonl_bytes(official_cases)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    checksum = _sha256_bytes(content)

    manifest = {
        "status": "frozen",
        "freeze_version": "v6",
        "official_corpus_created": True,
        "official_corpus_path": str(output),
        "official_corpus_sha256": checksum,
        "selection_policy": SELECTION_POLICY,
        "selection_performance_blind": True,
        "approved_total": 48,
        "official_selected": 45,
        "approved_reserve": 3,
        "reserve_ids": list(RESERVE_IDS),
        "selected_ids": [case.case_id for case in selected],
        "review_reports": review_reports,
        "input_sha256": {
            str(CONTEXT_VALIDATION_V6_DRAFT_PATH): _sha256_file(CONTEXT_VALIDATION_V6_DRAFT_PATH),
            **{
                str(path): _sha256_file(path)
                for pair in REVIEW_INPUTS
                for path in pair
            },
        },
        "validation": {
            "official_readiness": readiness,
            "all_approved_validation": validate_v6_draft(tuple(all_approved)),
            "selected_ids_unique": len({case.case_id for case in selected}) == 45,
            "reserve_ids_unique": len(set(RESERVE_IDS)) == 3,
            "rejected_or_pending_selected": False,
            "provenance_valid": True,
        },
        "composition": {
            "cases": len(official_cases),
            "mentions": sum(len(case.gold) for case in official_cases),
            "sources": readiness["sources"],
        },
        "blind_run": {
            "status": "pending",
            "repair_allowed_before_run": False,
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    print(json.dumps(freeze(output=args.output, manifest_path=args.manifest), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
