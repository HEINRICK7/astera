"""Composition and freeze rules for the future V6 corpus."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .models import BenchmarkCase, GoldMention


_RELATION_FIELDS = frozenset({
    "negated",
    "certainty",
    "temporality",
    "experiencer",
    "laterality",
    "dose",
    "dose_value",
    "dose_unit",
    "frequency",
    "route",
    "status",
})


def _validate_gold_provenance(case: BenchmarkCase, gold: GoldMention, segment_ids: set[str]) -> None:
    """Require segment-level provenance for every conversational gold."""
    if not case.segments:
        return
    if not gold.segment_ids:
        raise V6AssemblyBlocked(f"missing segment ownership: {case.case_id}/{gold.surface}")
    if not set(gold.segment_ids).issubset(segment_ids):
        raise V6AssemblyBlocked(f"unknown segment ownership: {case.case_id}/{gold.surface}")
    if "concept" not in gold.attribute_provenance:
        raise V6AssemblyBlocked(f"missing concept provenance: {case.case_id}/{gold.surface}")
    for name, sources in gold.attribute_provenance.items():
        if not sources or not set(sources).issubset(segment_ids):
            raise V6AssemblyBlocked(f"invalid attribute provenance: {case.case_id}/{gold.surface}/{name}")
    for name, sources in gold.relation_provenance.items():
        if name not in _RELATION_FIELDS:
            raise V6AssemblyBlocked(f"unknown relation provenance: {case.case_id}/{gold.surface}/{name}")
        if not sources or not set(sources).issubset(segment_ids):
            raise V6AssemblyBlocked(f"invalid relation provenance: {case.case_id}/{gold.surface}/{name}")
    for name in _RELATION_FIELDS.intersection(gold.attribute_provenance):
        if name not in gold.relation_provenance:
            raise V6AssemblyBlocked(f"missing relation provenance: {case.case_id}/{gold.surface}/{name}")


@dataclass(frozen=True, slots=True)
class V6Composition:
    total_cases: int = 150
    independent_cases: int = 60
    realistic_cases: int = 45
    simulator_cases: int = 45


class V6AssemblyBlocked(ValueError):
    """Raised when the official corpus is not yet eligible for assembly."""


def validate_v6_draft(
    cases: Sequence[BenchmarkCase],
    *,
    forbidden_texts: set[str] | None = None,
) -> dict[str, object]:
    """Validate a draft without calling it the official V6 corpus."""
    seen_ids: set[str] = set()
    seen_texts: set[str] = set()
    segment_count = 0
    mention_count = 0
    for case in cases:
        if case.case_id in seen_ids:
            raise V6AssemblyBlocked(f"duplicate V6 case_id: {case.case_id}")
        if case.text in seen_texts:
            raise V6AssemblyBlocked(f"duplicate V6 text: {case.case_id}")
        if forbidden_texts and case.text in forbidden_texts:
            raise V6AssemblyBlocked(f"V6 text overlaps a frozen prior corpus: {case.case_id}")
        seen_ids.add(case.case_id)
        seen_texts.add(case.text)
        segment_ids = {segment.segment_id for segment in case.segments}
        segment_count += len(segment_ids)
        mention_count += len(case.gold)
        for gold in case.gold:
            _validate_gold_provenance(case, gold, segment_ids)
    return {
        "cases": len(cases),
        "mentions": mention_count,
        "segments": segment_count,
        "sources": _source_counts(cases),
        "official": False,
    }


def assert_official_v6_ready(
    human_cases: Sequence[BenchmarkCase],
    approved_simulator_cases: Sequence[BenchmarkCase],
    *,
    forbidden_texts: set[str] | None = None,
    composition: V6Composition = V6Composition(),
) -> dict[str, object]:
    """Refuse assembly until human review supplies the simulator quota."""
    all_cases = tuple(human_cases) + tuple(approved_simulator_cases)
    report = validate_v6_draft(all_cases, forbidden_texts=forbidden_texts)
    source_counts = _source_counts(all_cases)
    expected = {
        "independent": composition.independent_cases,
        "realistic": composition.realistic_cases,
        "simulator-approved": composition.simulator_cases,
    }
    missing = {
        source: max(0, count - source_counts.get(source, 0))
        for source, count in expected.items()
    }
    if len(all_cases) != composition.total_cases or any(missing.values()):
        raise V6AssemblyBlocked(
            f"V6 requires human-reviewed simulator cases; missing={missing}, "
            f"actual_cases={len(all_cases)}"
        )
    return {**report, "official": True, "composition": expected}


def _source_counts(cases: Sequence[BenchmarkCase]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in cases:
        counts[case.source] = counts.get(case.source, 0) + 1
    return counts
