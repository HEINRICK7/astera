"""Validate V7 human annotations structurally without running the resolver."""
from __future__ import annotations

import hashlib
import json
import re
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DRAFT = DATA / "v7_unseen_generalization_draft.jsonl"
BATCH_DIR = RESULTS / "v7-adjudication-batches-2026-08-15"
OUTPUT = RESULTS / "v7-adjudication-validation-2026-08-15.json"
OUTPUT_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_HUMAN_ADJUDICATION_VALIDATION.md"
DECISIONS = {"APPROVED", "REJECTED", "AMBIGUOUS", "PENDING_HUMAN"}
POLICY_VERSION_ALIASES = {"1.2", "clinical-semantic-policy-v1.2", "1.3", "clinical-semantic-policy-v1.3"}
CONCEPT_ID = re.compile(r"^[a-z][a-z0-9_-]*\.[a-z][a-z0-9_-]*$")
FIELDS = {
    "surface", "concept_id", "negated", "certainty", "temporality", "experiencer",
    "laterality", "dose", "dose_value", "dose_unit", "frequency", "route", "status",
    "occurrence", "relations", "segment_ids", "attribute_provenance", "relation_provenance",
}
ATTR_FIELDS = {
    "negated", "certainty", "temporality", "experiencer", "laterality", "dose",
    "dose_value", "dose_unit", "frequency", "route", "status",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_draft(path: Path = DRAFT) -> dict[str, dict[str, Any]]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {record["case_id"]: record for record in records}


def _source_segments(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {segment["segment_id"]: segment for segment in record.get("segments", [])}


def _validate_gold(case: dict[str, Any], gold: Any) -> tuple[list[str], int, int, bool]:
    errors: list[str] = []
    segments = _source_segments(case)
    mentions = 0
    relations = 0
    provenance_valid = True
    if not isinstance(gold, list) or not gold:
        return ["approved gold must be a non-empty list"], 0, 0, False
    for mention_index, item in enumerate(gold):
        mentions += 1
        prefix = f"{case['case_id']}.gold[{mention_index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: mention must be an object")
            provenance_valid = False
            continue
        if not isinstance(item.get("surface"), str) or not item["surface"].strip():
            errors.append(f"{prefix}: surface is required")
        if not isinstance(item.get("concept_id"), str) or not CONCEPT_ID.fullmatch(item["concept_id"]):
            errors.append(f"{prefix}: invalid concept_id")
        unknown = set(item) - FIELDS
        if unknown:
            errors.append(f"{prefix}: unknown fields {sorted(unknown)}")
        segment_ids = item.get("segment_ids")
        if not isinstance(segment_ids, list) or not segment_ids:
            errors.append(f"{prefix}: segment_ids must be a non-empty list")
            provenance_valid = False
            segment_ids = []
        missing_segments = [segment_id for segment_id in segment_ids if segment_id not in segments]
        if missing_segments:
            errors.append(f"{prefix}: missing segment_ids {missing_segments}")
            provenance_valid = False
        surface = str(item.get("surface", ""))
        if not any(surface.casefold() in segments[segment_id]["text"].casefold() for segment_id in segment_ids if segment_id in segments):
            errors.append(f"{prefix}: surface does not exist in an owned segment")
        if isinstance(item.get("relations", []), list):
            relations += len(item.get("relations", []))
            endpoints = {surface, item.get("concept_id"), *ATTR_FIELDS}
            for relation_index, relation in enumerate(item.get("relations", [])):
                relation_prefix = f"{prefix}.relations[{relation_index}]"
                if not isinstance(relation, dict):
                    errors.append(f"{relation_prefix}: relation must be an object")
                    continue
                if not isinstance(relation.get("relation_type"), str) or not relation["relation_type"]:
                    errors.append(f"{relation_prefix}: relation_type is required")
                if relation.get("source") is not None and relation.get("source") not in endpoints:
                    errors.append(f"{relation_prefix}: source endpoint is not an annotated entity")
                if relation.get("target") not in endpoints:
                    errors.append(f"{relation_prefix}: target endpoint is not an annotated entity")
        else:
            errors.append(f"{prefix}: relations must be a list")
        for field_name, value in item.items():
            if field_name in ATTR_FIELDS and value is not None and not isinstance(value, (str, bool, int, float)):
                errors.append(f"{prefix}: attribute {field_name} has invalid schema type")
        for provenance_name in ("attribute_provenance", "relation_provenance"):
            provenance = item.get(provenance_name, {})
            if not isinstance(provenance, dict):
                errors.append(f"{prefix}: {provenance_name} must be an object")
                provenance_valid = False
                continue
            for field_name, source_ids in provenance.items():
                if not isinstance(source_ids, list) or not set(source_ids).issubset(segments):
                    errors.append(f"{prefix}: {provenance_name}.{field_name} references unknown segments")
                    provenance_valid = False
    return errors, mentions, relations, provenance_valid and not errors


def _consistency(approved: list[dict[str, Any]]) -> dict[str, Any]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for item in approved:
        group = item.get("semantic_equivalence_group")
        if not group or item.get("gold") is None:
            continue
        signature = json.dumps(item["gold"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        groups[str(group)].append(signature)
    if not groups:
        return {"status": "NOT_COMPUTABLE_NO_GROUPS", "groups": 0, "consistent_groups": 0, "rate": None}
    consistent = sum(len(set(signatures)) == 1 for signatures in groups.values())
    return {"status": "COMPUTED", "groups": len(groups), "consistent_groups": consistent, "rate": consistent / len(groups)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-file",
        type=Path,
        help="validate one adjudicated batch without changing the official queue",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="JSON report path; defaults to the official full-queue report",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Markdown report path; defaults to the official full-queue report",
    )
    args = parser.parse_args()

    draft = _load_draft()
    batch_paths = [args.batch_file] if args.batch_file else sorted(BATCH_DIR.glob("v7-batch-*.json"))
    all_reviews: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_case_ids: set[str] = set()
    for path in batch_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for review in payload.get("reviews", []):
            all_reviews.append(review)
            case_id = review.get("candidate_id")
            if case_id in seen_case_ids:
                errors.append(f"{path.name}: duplicate candidate_id {case_id}")
            seen_case_ids.add(case_id)
            if case_id not in draft:
                errors.append(f"{path.name}: unknown candidate_id {case_id}")
                continue
            decision = review.get("decision")
            if decision not in DECISIONS:
                errors.append(f"{case_id}: invalid decision {decision}")
                continue
            if review.get("policy_version") not in POLICY_VERSION_ALIASES:
                errors.append(f"{case_id}: policy_version must identify clinical semantic policy v1.2")
            if decision == "PENDING_HUMAN":
                if review.get("gold") is not None:
                    errors.append(f"{case_id}: pending review cannot contain gold")
                continue
            if decision == "APPROVED":
                if not str(review.get("reviewer", "")).strip():
                    errors.append(f"{case_id}: approved review requires reviewer")
                gold_errors, _, _, _ = _validate_gold(draft[case_id], review.get("gold"))
                errors.extend(f"{case_id}: {error}" for error in gold_errors)
            elif review.get("gold") is not None:
                errors.append(f"{case_id}: {decision} review must not create gold")
    counts = Counter(review.get("decision") for review in all_reviews)
    approved = [review for review in all_reviews if review.get("decision") == "APPROVED"]
    mentions = relations = 0
    provenance_valid_count = 0
    cross_segment_cases = 0
    for review in approved:
        case = draft[review["candidate_id"]]
        _, mention_count, relation_count, provenance_valid = _validate_gold(case, review.get("gold"))
        mentions += mention_count
        relations += relation_count
        provenance_valid_count += int(provenance_valid)
        if any(len(item.get("segment_ids", [])) > 1 for item in review.get("gold", [])):
            cross_segment_cases += 1
    pending = counts.get("PENDING_HUMAN", 0)
    is_batch = args.batch_file is not None
    output = args.output or OUTPUT
    output_md = args.output_md or OUTPUT_MD
    observed_policy_versions = sorted({
        str(review.get("policy_version"))
        for review in all_reviews
        if review.get("policy_version") in POLICY_VERSION_ALIASES
    })
    report_policy_version = "1.3" if any("1.3" in value for value in observed_policy_versions) else "1.2"
    report = {
        "status": "HUMAN_GATE",
        "scope": "BATCH" if is_batch else "FULL_QUEUE",
        "validated_batch_file": str(args.batch_file) if is_batch else None,
        "policy_version": report_policy_version,
        "total": len(all_reviews) if is_batch else len(draft),
        "case_count": len(all_reviews) if is_batch else len(draft),
        "batch_count": len(batch_paths),
        "decision_counts": {decision: counts.get(decision, 0) for decision in sorted(DECISIONS)},
        "mentions": mentions,
        "relations": relations,
        "cross_segment_cases": cross_segment_cases if approved else None,
        "provenance_valid": provenance_valid_count if approved else None,
        "provenance_valid_total_approved": len(approved),
        "adjudication_consistency": _consistency(all_reviews),
        "structural_errors": errors,
        "structural_validation_passed": not errors,
        "pending_before_freeze": pending,
        "human_review_complete": pending == 0 and not errors,
        "gold_validation_complete": pending == 0 and not errors and bool(approved),
        "corpus_freeze_complete": False,
        "resolver_executed": False,
        "official_v7_run": False,
        "blind_run": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
        "next_action": "continue-human-adjudication" if pending else "human-gate-before-freeze",
        "draft_sha256": _sha256(DRAFT),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(
        "# V7 Human Gold Adjudication Validation\n\n"
        "Status: **HUMAN GATE**\n\n"
        f"Policy: `v{report['policy_version']}`  \n"
        f"Total cases: `{report['total']}`  \n"
        f"Batches: `{report['batch_count']}`  \n"
        f"APPROVED: `{report['decision_counts']['APPROVED']}`  \n"
        f"REJECTED: `{report['decision_counts']['REJECTED']}`  \n"
        f"AMBIGUOUS: `{report['decision_counts']['AMBIGUOUS']}`  \n"
        f"PENDING_HUMAN: `{report['decision_counts']['PENDING_HUMAN']}`  \n\n"
        "The validator checks only structural properties and never executes the resolver or infers semantic gold.\n\n"
        f"- structural validation: `{'PASS' if report['structural_validation_passed'] else 'FAIL'}`\n"
        f"- provenance valid: `{report['provenance_valid'] if report['provenance_valid'] is not None else 'NOT_COMPUTABLE_PENDING_HUMAN'}`\n"
        f"- adjudication consistency: `{report['adjudication_consistency']['status']}`\n"
        "- corpus freeze: `NOT_AUTHORIZED`\n"
        "- blind run: `BLOCKED`\n"
        "- resolver executed: `false`\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "scope": report["scope"], "counts": report["decision_counts"], "structural_errors": len(errors), "output": str(output)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
