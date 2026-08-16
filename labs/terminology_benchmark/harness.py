"""Reproducible terminology/entity-linking benchmark harness."""
from __future__ import annotations

import json
import math
import resource
from statistics import mean
from time import perf_counter, process_time
from typing import Iterable

from .adapters import BenchmarkAdapter
from .corpus import load_corpus, mention_span
from .models import BenchmarkAnnotation, BenchmarkCase, BenchmarkReport


WEIGHTS = {
    "clinical_accuracy": 0.40,
    "pt_br_robustness": 0.20,
    "cpu_ram": 0.15,
    "operational_simplicity": 0.10,
    "licensing": 0.10,
    "maintainability": 0.05,
}


def run(adapter: BenchmarkAdapter, cases: Iterable[BenchmarkCase] | None = None) -> BenchmarkReport:
    corpus = tuple(cases or load_corpus())
    started = perf_counter()
    cpu_started = process_time()
    observations: list[tuple[BenchmarkCase, tuple[BenchmarkAnnotation, ...], float]] = []
    stable_runs: list[bool] = []
    for case in corpus:
        case_started = perf_counter()
        first = adapter.annotate(case.text, language=case.language)
        second = adapter.annotate(case.text, language=case.language)
        observations.append((case, first, (perf_counter() - case_started) * 1000))
        stable_runs.append(_signature(first) == _signature(second))

    tp = fp = fn = 0
    linked = 0
    attribute_matches: dict[str, int] = {}
    attribute_total: dict[str, int] = {}
    provenance_values: list[bool] = []
    for case, annotations, _ in observations:
        used: set[int] = set()
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface)
            match_index = next(
                (index for index, item in enumerate(annotations)
                 if index not in used and item.start == start and item.end == end),
                None,
            )
            if match_index is None:
                fn += 1
                continue
            used.add(match_index)
            tp += 1
            item = annotations[match_index]
            if item.concept_id == gold.concept_id:
                linked += 1
            for name in ("negated", "certainty", "temporality", "experiencer", "laterality", "dose"):
                expected = getattr(gold, name)
                actual = getattr(item, name)
                if expected is None and actual is None:
                    continue
                attribute_total[name] = attribute_total.get(name, 0) + 1
                attribute_matches[name] = attribute_matches.get(name, 0) + int(actual == expected)
            provenance_values.append(_has_provenance(item))
        fp += len(annotations) - len(used)

    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    linking = _ratio(linked, tp)
    false_positive_rate = _ratio(fp, fp + tp)
    attributes = {
        name: _ratio(attribute_matches.get(name, 0), total)
        for name, total in attribute_total.items()
    }
    critical = [attributes.get(name, 0.0) for name in ("negated", "certainty", "dose")]
    provenance = mean(provenance_values) if provenance_values else 0.0
    elapsed = (perf_counter() - started) * 1000
    latency_values = sorted(item[2] for item in observations)
    latency = {
        "mean": mean(latency_values) if latency_values else 0.0,
        "p50": _percentile(latency_values, 0.50),
        "p95": _percentile(latency_values, 0.95),
        "total": elapsed,
    }
    clinical_accuracy = (precision + recall + linking) / 3
    pt_br_robustness = recall * ((sum(attributes.values()) / len(attributes)) if attributes else 0.0)
    cpu_ram = 1.0 / (1.0 + process_time() - cpu_started)
    score = (
        clinical_accuracy * WEIGHTS["clinical_accuracy"]
        + pt_br_robustness * WEIGHTS["pt_br_robustness"]
        + cpu_ram * WEIGHTS["cpu_ram"]
        + _operational_score(adapter) * WEIGHTS["operational_simplicity"]
        + _licensing_score(adapter) * WEIGHTS["licensing"]
        + 1.0 * WEIGHTS["maintainability"]
    )
    return BenchmarkReport(
        provider=adapter.metadata,
        cases=len(corpus),
        entity_precision=precision,
        entity_recall=recall,
        linking_accuracy=linking,
        false_positive_rate=false_positive_rate,
        attribute_accuracy={**attributes, "provenance": provenance},
        provenance_completeness=provenance,
        concept_stability=mean(stable_runs) if stable_runs else 0.0,
        latency_ms=latency,
        cpu_seconds=process_time() - cpu_started,
        rss_bytes=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024,
        startup_seconds=adapter.startup_seconds,
        weighted_score=score,
        hard_gate_passed=all(value >= 1.0 for value in critical) and provenance >= 1.0,
    )


def print_report(report: BenchmarkReport) -> None:
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))


def _signature(items: tuple[BenchmarkAnnotation, ...]) -> tuple[tuple[object, ...], ...]:
    return tuple((item.start, item.end, item.concept_id, item.surface) for item in items)


def _has_provenance(item: BenchmarkAnnotation) -> bool:
    return all(item.provenance.get(key) for key in ("provider", "source_text"))


def _ratio(numerator: int | float, denominator: int | float) -> float:
    return float(numerator) / float(denominator) if denominator else 0.0


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, max(0, math.ceil(len(values) * percentile) - 1))
    return values[index]


def _operational_score(adapter: BenchmarkAdapter) -> float:
    return 1.0 if adapter.metadata.asset_bytes is None or adapter.metadata.asset_bytes < 2_000_000_000 else 0.5


def _licensing_score(adapter: BenchmarkAdapter) -> float:
    required = (adapter.metadata.code_license, adapter.metadata.data_license, adapter.metadata.model_license)
    return 1.0 if all(value and "UNSET" not in value for value in required) else 0.0
