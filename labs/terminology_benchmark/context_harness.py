"""Evaluation harness for the separate Clinical Context track."""
from __future__ import annotations

import asyncio
import json
from collections import Counter
from statistics import mean
from time import perf_counter

from apps.runtime.src.ports.outbound.clinical_semantics import (
    ClinicalContextPort,
    ClinicalContextQuery,
)

from .corpus import load_corpus, mention_span
from .models import BenchmarkCase


async def evaluate(
    adapter: ClinicalContextPort,
    cases: tuple[BenchmarkCase, ...] | None = None,
    *,
    enforce_composition_gate: bool = False,
    composition_thresholds: dict[str, float] | None = None,
    semantic_policy: str | None = None,
) -> dict[str, object]:
    cases = cases or load_corpus()
    totals: Counter[str] = Counter()
    matches: Counter[str] = Counter()
    provenance = 0
    provenance_total = 0
    mention_exact_matches = 0
    mention_exact_total = 0
    relation_exact_matches = 0
    relation_exact_total = 0
    scope_matches = 0
    scope_total = 0
    multi_mention_cases = 0
    isolated_multi_mention_cases = 0
    latencies: list[float] = []
    for case in cases:
        case_mentions_exact = True
        if len(case.gold) > 1:
            multi_mention_cases += 1
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            started = perf_counter()
            result = await adapter.analyze(
                ClinicalContextQuery(
                    text=case.text,
                    language=case.language,
                    start=start,
                    end=end,
                    evidence_id=case.case_id,
                    semantic_policy=semantic_policy,
                )
            )
            latencies.append((perf_counter() - started) * 1000)
            critical_fields = (
                "negated", "certainty", "temporality", "experiencer", "laterality",
                "dose", "dose_value", "dose_unit", "frequency", "route", "status",
            )
            mention_exact_total += 1
            mention_is_exact = all(
                getattr(result, field) == getattr(gold, field)
                for field in critical_fields
            )
            mention_exact_matches += int(mention_is_exact)
            case_mentions_exact = case_mentions_exact and mention_is_exact
            scope_fields = ("negated", "certainty", "temporality", "experiencer", "laterality")
            scope_total += len(scope_fields)
            scope_matches += sum(getattr(result, field) == getattr(gold, field) for field in scope_fields)
            actual_relations = _actual_relations(result)
            expected_relations = _expected_relations(gold)
            if expected_relations:
                relation_exact_total += 1
                relation_exact_matches += int(actual_relations == expected_relations)
            for field in (
                "negated", "certainty", "temporality", "experiencer", "laterality",
                "dose", "dose_value", "dose_unit", "frequency", "route", "status",
            ):
                expected = getattr(gold, field)
                actual = getattr(result, field)
                if expected is None and actual is None:
                    continue
                totals[field] += 1
                matches[field] += int(expected == actual)
            provenance_total += 1
            provenance += int(bool(result.provenance.get("provider") and result.provenance.get("source_text")))
        if len(case.gold) > 1 and case_mentions_exact:
            isolated_multi_mention_cases += 1
    metrics = {field: _ratio(matches[field], totals[field]) for field in totals}
    metrics["provenance"] = _ratio(provenance, provenance_total)
    metrics["mention_exact_match"] = _ratio(mention_exact_matches, mention_exact_total)
    metrics["relation_exact_match"] = (
        _ratio(relation_exact_matches, relation_exact_total)
        if relation_exact_total
        else 1.0
    )
    metrics["scope_accuracy"] = _ratio(scope_matches, scope_total)
    metrics["cross_mention_isolation"] = (
        _ratio(isolated_multi_mention_cases, multi_mention_cases)
        if multi_mention_cases
        else 1.0
    )
    thresholds = {
        "negated": 0.90,
        "certainty": 0.90,
        "temporality": 0.90,
        "experiencer": 0.95,
        "dose": 0.90,
        "provenance": 1.0,
        "mention_exact_match": 0.90,
    }
    if enforce_composition_gate:
        thresholds.update(composition_thresholds or {
            "relation_exact_match": 0.90,
            "scope_accuracy": 0.90,
            "cross_mention_isolation": 0.90,
        })
    return {
        "provider": getattr(adapter, "provider", type(adapter).__name__),
        "metadata": _metadata(adapter),
        "cases": len(cases),
        "attribute_accuracy": metrics,
        "hard_gate_thresholds": thresholds,
        "mean_latency_ms": mean(latencies) if latencies else 0.0,
        "startup_seconds": getattr(adapter, "startup_seconds", 0.0),
        "hard_gate_passed": all(
            metrics.get(field, 0.0) >= threshold
            for field, threshold in thresholds.items()
        ),
    }


def print_baseline() -> None:
    from .context_adapters import DeterministicContextAdapter

    print(json.dumps(asyncio.run(evaluate(DeterministicContextAdapter())), ensure_ascii=False, indent=2))


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _expected_relations(gold: object) -> tuple[tuple[str, str, str | None], ...]:
    expected = {(relation.relation_type, relation.target, relation.value) for relation in gold.relations}
    if gold.dose:
        expected.add(("HAS_DOSE", "dose", gold.dose))
    if gold.frequency:
        expected.add(("HAS_FREQUENCY", "frequency", gold.frequency))
    if gold.route:
        expected.add(("HAS_ROUTE", "route", gold.route))
    if gold.laterality:
        expected.add(("HAS_LATERALITY", "laterality", gold.laterality))
    if gold.status == "discontinued":
        expected.add(("DISCONTINUED_AT", "status", "discontinued"))
    return tuple(sorted(expected))


def _actual_relations(result: object) -> tuple[tuple[str, str, str | None], ...]:
    projection = getattr(result, "provenance", {}).get("projection", {})
    return tuple(
        sorted(
            (
                relation.get("relation_type"),
                relation.get("target"),
                relation.get("value"),
            )
            for relation in projection.get("relations", ())
        )
    )


def _metadata(adapter: ClinicalContextPort) -> dict[str, object] | None:
    metadata = getattr(adapter, "metadata", None)
    if metadata is None:
        return None
    return {
        "code_license": metadata.code_license,
        "data_license": metadata.data_license,
        "model_license": metadata.model_license,
        "vocabulary": metadata.vocabulary,
        "vocabulary_version": metadata.vocabulary_version,
        "source_uri": metadata.source_uri,
        "model_path": metadata.model_path,
        "asset_bytes": metadata.asset_bytes,
        "asset_sha256": metadata.asset_sha256,
        "notes": metadata.notes,
    }
