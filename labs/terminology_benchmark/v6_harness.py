"""Validation harness for the draft V6, including conversation metrics."""
from __future__ import annotations

from collections import Counter
from time import perf_counter

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextPort, ClinicalContextQuery

from .context_harness import evaluate
from .corpus import mention_span
from .models import BenchmarkCase


async def evaluate_v6(
    adapter: ClinicalContextPort,
    cases: tuple[BenchmarkCase, ...],
    *,
    semantic_policy: str | None = "clinical-semantic-policy-v1.1",
) -> dict[str, object]:
    base = await evaluate(
        adapter,
        cases,
        enforce_composition_gate=True,
        semantic_policy=semantic_policy,
        composition_thresholds={
            "relation_exact_match": 0.95,
            "scope_accuracy": 0.97,
            "cross_mention_isolation": 0.95,
        },
    )
    conversation_cases = [case for case in cases if case.segments]
    segment_total = 0
    segment_matches = 0
    speaker_total = 0
    speaker_matches = 0
    latencies: list[float] = []
    fields = (
        "negated", "certainty", "temporality", "experiencer", "laterality",
        "dose", "dose_value", "dose_unit", "frequency", "route", "status",
    )
    for case in conversation_cases:
        for gold in case.gold:
            if not gold.segment_ids:
                continue
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
            segment_total += 1
            segment_matches += int(all(getattr(result, field) == getattr(gold, field) for field in fields))
            speaker_total += 1
            speaker_matches += int(result.experiencer == gold.experiencer)
    v6_metrics = {
        "conversation_cases": len(conversation_cases),
        "cross_segment_resolution": segment_matches / segment_total if segment_total else 1.0,
        "speaker_attribution": speaker_matches / speaker_total if speaker_total else 1.0,
        "cross_segment_mentions": segment_total,
        "cross_segment_mean_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
    }
    base["v6_metrics"] = v6_metrics
    base["hard_gate_thresholds"].update({
        "cross_segment_resolution": 0.90,
        "speaker_attribution": 0.95,
    })
    base["hard_gate_passed"] = base["hard_gate_passed"] and all(
        v6_metrics[field] >= threshold
        for field, threshold in {
            "cross_segment_resolution": 0.90,
            "speaker_attribution": 0.95,
        }.items()
    )
    return base
