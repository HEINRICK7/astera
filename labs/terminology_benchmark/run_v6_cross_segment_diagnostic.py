"""Decompose the frozen V6 blind-run failures by cross-segment pattern."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus


ROOT = Path(__file__).parent
DEFAULT_BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
DEFAULT_TAXONOMY = ROOT / "results" / "context-taxonomy-v6-blind-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-cross-segment-taxonomy-v6-2026-08-15.json"


def diagnose(*, corpus_path: Path, blind_path: Path, taxonomy_path: Path) -> dict[str, object]:
    blind = json.loads(blind_path.read_text(encoding="utf-8"))
    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    cases = {case.case_id: case for case in load_corpus(corpus_path)}
    conversation_cases = {case_id: case for case_id, case in cases.items() if case.segments}
    composition = taxonomy.get("report", {}).get("composition", {})
    details = composition.get("details", ())
    cross_details = [detail for detail in details if detail.get("case_id") in conversation_cases]

    mismatch_fields: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    case_error_types: defaultdict[str, set[str]] = defaultdict(set)
    for detail in cross_details:
        case_id = str(detail["case_id"])
        for field in detail.get("mismatches", ()):
            mismatch_fields[field] += 1
            category = {
                "experiencer": "EXPERIENCER_CARRY_OVER",
                "laterality": "LATERALITY_CARRY_OVER",
                "dose": "DOSE_CARRY_OVER",
                "dose_value": "DOSE_CARRY_OVER",
                "dose_unit": "DOSE_CARRY_OVER",
                "status": "STATUS_CARRY_OVER",
                "temporality": "TEMPORAL_CARRY_OVER",
                "negated": "NEGATION_CARRY_OVER",
            }.get(field, "LOCAL_OR_COMPOSITION_ERROR")
            category_counts[category] += 1
            case_error_types[case_id].add(category)

    cross_segment_gold = sum(
        1
        for case in conversation_cases.values()
        for gold in case.gold
        if len(gold.segment_ids) > 1
    )
    cross_segment_case_counts = Counter()
    for case_id, error_types in case_error_types.items():
        for error_type in error_types:
            cross_segment_case_counts[error_type] += 1

    v6_metrics = blind.get("report", {}).get("v6_metrics", {})
    result = {
        "status": "diagnosed",
        "corpus": corpus_path.stem,
        "official_corpus": True,
        "blind_run": str(blind_path),
        "taxonomy": str(taxonomy_path),
        "conversation_cases": len(conversation_cases),
        "conversation_mentions": sum(len(case.gold) for case in conversation_cases.values()),
        "cross_segment_gold_mentions": cross_segment_gold,
        "cross_segment_resolution": v6_metrics.get("cross_segment_resolution"),
        "speaker_attribution": v6_metrics.get("speaker_attribution"),
        "cross_segment_mismatch_fields": dict(mismatch_fields),
        "cross_segment_error_categories": dict(category_counts),
        "cases_by_error_category": dict(cross_segment_case_counts),
        "cases_with_cross_segment_errors": len(case_error_types),
        "diagnostic_only": True,
        "repair_applied": False,
        "holdout_ids_excluded": ["sim-v6-0056", "sim-v6-0057", "sim-v6-0058"],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--blind", type=Path, default=DEFAULT_BLIND)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = diagnose(corpus_path=args.corpus, blind_path=args.blind, taxonomy_path=args.taxonomy)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
