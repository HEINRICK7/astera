"""Analyze residual V6 errors after cross-segment repair v1."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_harness import _actual_relations, _expected_relations
from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus, mention_span
from .cross_segment_context import CrossSegmentContextAdapter
from .models import BenchmarkCase, GoldMention


ROOT = Path(__file__).parent
DEFAULT_BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
DEFAULT_REPAIR = ROOT / "results" / "context-validation-v6-cross-segment-repair-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-cross-segment-residual-analysis-v6-2026-08-15.json"
HOLDOUT_IDS = {"sim-v6-0056", "sim-v6-0057", "sim-v6-0058"}
RESIDUAL_CATEGORIES = (
    "STATUS_CARRY_OVER",
    "TEMPORAL_CARRY_OVER",
    "LATERALITY_CARRY_OVER",
    "NEGATION_CARRY_OVER",
    "DOSE_CARRY_OVER",
    "EXPERIENCER_CARRY_OVER",
    "REFERENCE_RESOLUTION",
    "RELATION_MISSING",
    "RELATION_WRONG_TARGET",
    "RELATION_WRONG_SOURCE",
    "CONTEXT_OVERWRITE",
    "CONTEXT_STALE",
    "AMBIGUOUS_ANTECEDENT",
    "WRONG_SEGMENT_PROVENANCE",
)
ARCHITECTURE_AREAS = (
    "CONTEXT_STATE",
    "REFERENCE_RESOLUTION",
    "ATTRIBUTE_ATTACHMENT",
    "RELATION_RESOLUTION",
)
FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "dose", "dose_value", "dose_unit", "frequency", "route", "status",
)
FIELD_CATEGORIES = {
    "status": "STATUS_CARRY_OVER",
    "temporality": "TEMPORAL_CARRY_OVER",
    "laterality": "LATERALITY_CARRY_OVER",
    "negated": "NEGATION_CARRY_OVER",
    "dose": "DOSE_CARRY_OVER",
    "dose_value": "DOSE_CARRY_OVER",
    "dose_unit": "DOSE_CARRY_OVER",
    "experiencer": "EXPERIENCER_CARRY_OVER",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _segment_for_span(case: BenchmarkCase, start: int) -> str | None:
    cursor = 0
    for segment in case.segments:
        segment_start = case.text.find(segment.text, cursor)
        if segment_start >= 0 and segment_start <= start <= segment_start + len(segment.text):
            return segment.segment_id
        if segment_start >= 0:
            cursor = segment_start + len(segment.text)
    return None


def _provenance_mismatch(gold: GoldMention, repaired: Any) -> bool:
    actual = repaired.provenance.get("segment_provenance", {})
    for field, expected in gold.attribute_provenance.items():
        if field in actual and tuple(actual[field]) != tuple(expected):
            return True
    return False


def _representative(item: dict[str, object]) -> dict[str, object]:
    return {
        "case_id": item["case_id"],
        "surface": item["surface"],
        "text": item["text"],
        "segments": item["segments"],
        "mismatches": item["mismatches"],
        "expected_relations": item["expected_relations"],
        "actual_relations": item["actual_relations"],
    }


async def analyze(*, corpus_path: Path, blind_path: Path, repair_path: Path) -> dict[str, object]:
    blind = json.loads(blind_path.read_text(encoding="utf-8"))
    repair = json.loads(repair_path.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != blind.get("official_corpus_sha256") or checksum != repair.get("official_corpus_sha256"):
        raise RuntimeError("residual analysis input is not the frozen V6 corpus")
    cases = load_corpus(corpus_path)
    if any(case.case_id in HOLDOUT_IDS for case in cases):
        raise RuntimeError("holdout cases must not participate in residual analysis")

    baseline_adapter = NieDEPtBrSafetyRules()
    repaired_adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    residual_field_counts: Counter[str] = Counter()
    residual_categories: Counter[str] = Counter()
    architecture_categories: Counter[str] = Counter()
    examples: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    relation_counts: Counter[str] = Counter()
    cross_relation_counts: Counter[str] = Counter()
    mention_counts = {"baseline_exact": 0, "repair_exact": 0, "total": 0}
    case_error_types: defaultdict[str, set[str]] = defaultdict(set)

    for case in cases:
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            query = ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
            )
            baseline = await baseline_adapter.analyze(query)
            repaired = await repaired_adapter.analyze(query)
            baseline_mismatches = [field for field in FIELDS if getattr(baseline, field) != getattr(gold, field)]
            repaired_mismatches = [field for field in FIELDS if getattr(repaired, field) != getattr(gold, field)]
            mention_counts["total"] += 1
            mention_counts["baseline_exact"] += int(not baseline_mismatches)
            mention_counts["repair_exact"] += int(not repaired_mismatches)

            expected_relations = _expected_relations(gold)
            baseline_relations = _actual_relations(baseline)
            repaired_relations = _actual_relations(repaired)
            if expected_relations:
                relation_counts["expected"] += 1
                relation_counts["baseline_exact"] += int(baseline_relations == expected_relations)
                relation_counts["repair_exact"] += int(repaired_relations == expected_relations)
                if repaired_relations != expected_relations:
                    relation_counts["RELATION_MISSING"] += int(
                        bool(set(expected_relations) - set(repaired_relations))
                    )
                    relation_counts["RELATION_WRONG_TARGET"] += int(
                        any(
                            expected[0] == actual[0] and expected[2] != actual[2]
                            for expected in expected_relations
                            for actual in repaired_relations
                        )
                    )

            is_conversational = len(case.segments) > 1
            is_cross_reference = len(gold.segment_ids) > 1
            if expected_relations and is_cross_reference:
                cross_relation_counts["expected"] += 1
                cross_relation_counts["repair_exact"] += int(repaired_relations == expected_relations)
                if repaired_relations != expected_relations:
                    cross_relation_counts["RELATION_MISSING"] += int(
                        bool(set(expected_relations) - set(repaired_relations))
                    )
                    cross_relation_counts["RELATION_WRONG_TARGET"] += int(
                        any(
                            expected[0] == actual[0] and expected[2] != actual[2]
                            for expected in expected_relations
                            for actual in repaired_relations
                        )
                    )
            if is_conversational and (is_cross_reference or repaired_mismatches):
                if repaired_mismatches:
                    for field in repaired_mismatches:
                        residual_field_counts[field] += 1
                        category = FIELD_CATEGORIES.get(field, "ATTRIBUTE_ATTACHMENT")
                        residual_categories[category] += 1
                        case_error_types[case.case_id].add(category)
                if repaired.provenance.get("context_state") and repaired_mismatches:
                    architecture_categories["CONTEXT_STATE"] += 1
                if is_cross_reference and repaired_mismatches:
                    architecture_categories["REFERENCE_RESOLUTION"] += 1
                if is_cross_reference and expected_relations and repaired_relations != expected_relations:
                    architecture_categories["RELATION_RESOLUTION"] += 1
                    residual_categories["RELATION_MISSING"] += int(
                        bool(set(expected_relations) - set(repaired_relations))
                    )
                    residual_categories["RELATION_WRONG_TARGET"] += int(
                        any(
                            expected[0] == actual[0] and expected[2] != actual[2]
                            for expected in expected_relations
                            for actual in repaired_relations
                        )
                    )
                if _provenance_mismatch(gold, repaired):
                    residual_categories["WRONG_SEGMENT_PROVENANCE"] += 1
                    architecture_categories["ATTRIBUTE_ATTACHMENT"] += 1

                item = {
                    "case_id": case.case_id,
                    "surface": gold.surface,
                    "text": case.text,
                    "segments": [segment.segment_id for segment in case.segments],
                    "mismatches": {
                        "baseline": baseline_mismatches,
                        "repair": repaired_mismatches,
                    },
                    "expected_relations": expected_relations,
                    "actual_relations": {
                        "baseline": baseline_relations,
                        "repair": repaired_relations,
                    },
                }
                for field in repaired_mismatches:
                    category = FIELD_CATEGORIES.get(field, "ATTRIBUTE_ATTACHMENT")
                    if len(examples[category]) < 3:
                        examples[category].append(_representative(item))

                if is_cross_reference and repaired_mismatches:
                    if not baseline_mismatches:
                        residual_categories["CONTEXT_OVERWRITE"] += 1
                    elif baseline_mismatches == repaired_mismatches:
                        residual_categories["CONTEXT_STALE"] += 1
                    elif not gold.segment_ids:
                        residual_categories["AMBIGUOUS_ANTECEDENT"] += 1
                if expected_relations and repaired_relations != expected_relations:
                    if len(examples["RELATION_RESOLUTION"]) < 3:
                        examples["RELATION_RESOLUTION"].append(_representative(item))

    result = {
        "status": "executed",
        "run_type": "v6-cross-segment-residual-analysis",
        "corpus": corpus_path.stem,
        "official_corpus": True,
        "official_corpus_sha256": checksum,
        "blind_baseline_path": str(blind_path),
        "repair_result_path": str(repair_path),
        "repair_version": "v1",
        "repair_applied": False,
        "holdout_ids_excluded": sorted(HOLDOUT_IDS),
        "mention_counts": mention_counts,
        "relation_counts": dict(relation_counts),
        "cross_segment_relation_counts": dict(cross_relation_counts),
        "residual_field_counts": dict(residual_field_counts),
        "residual_error_categories": {
            category: residual_categories.get(category, 0)
            for category in RESIDUAL_CATEGORIES
        },
        "architecture_area_counts": {
            area: architecture_categories.get(area, 0)
            for area in ARCHITECTURE_AREAS
        },
        "cases_by_error_category": {
            category: sum(category in types for types in case_error_types.values())
            for category in sorted({error for types in case_error_types.values() for error in types})
        },
        "examples": dict(examples),
        "metrics_comparison": {
            "baseline": blind["report"],
            "repair_v1": repair["repaired"],
        },
        "next_step": "design-second-repair-after-residual-analysis",
        "shadow_integration": False,
        "production_promotion": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--blind", type=Path, default=DEFAULT_BLIND)
    parser.add_argument("--repair", type=Path, default=DEFAULT_REPAIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = asyncio.run(analyze(corpus_path=args.corpus, blind_path=args.blind, repair_path=args.repair))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=list) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=list))


if __name__ == "__main__":
    main()
