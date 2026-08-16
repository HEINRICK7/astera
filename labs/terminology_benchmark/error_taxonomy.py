"""Error taxonomy and co-occurrence analysis for compositional validation."""
from __future__ import annotations

from collections import Counter
from typing import Iterable

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextPort, ClinicalContextQuery

from .corpus import mention_span
from .models import BenchmarkCase


ERROR_TYPES = (
    "ENTITY_MISBOUND",
    "ATTRIBUTE_MISBOUND",
    "NEGATION_SCOPE",
    "TEMPORAL_SCOPE",
    "FAMILY_EXPERIENCER_SCOPE",
    "DOSE_ATTACHMENT",
    "LATERALITY_ATTACHMENT",
    "STATUS_CONFLICT",
    "MULTI_MENTION_COLLISION",
    "RULE_PRECEDENCE",
)


async def analyze(adapter: ClinicalContextPort, cases: Iterable[BenchmarkCase]) -> dict[str, object]:
    error_counts: Counter[str] = Counter()
    cooccurrences: Counter[str] = Counter()
    details: list[dict[str, object]] = []
    case_classifications: list[dict[str, object]] = []
    cases_total = 0
    cases_with_errors = 0
    mention_total = 0
    exact_total = 0

    for case in cases:
        cases_total += 1
        case_errors: set[str] = set()
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface)
            result = await adapter.analyze(
                ClinicalContextQuery(
                    text=case.text,
                    language=case.language,
                    start=start,
                    end=end,
                    evidence_id=case.case_id,
                )
            )
            mention_total += 1
            fields = (
                "negated", "certainty", "temporality", "experiencer", "laterality",
                "dose", "dose_value", "dose_unit", "frequency", "route", "status",
            )
            mismatches = [
                field for field in fields
                if getattr(gold, field) != getattr(result, field)
            ]
            exact_total += int(not mismatches)
            for field in mismatches:
                error_type = _error_type(field)
                error_counts[error_type] += 1
                case_errors.add(error_type)
            if mismatches:
                details.append(
                    {
                        "case_id": case.case_id,
                        "surface": gold.surface,
                        "mismatches": mismatches,
                        "expected": {field: getattr(gold, field) for field in mismatches},
                        "actual": {field: getattr(result, field) for field in mismatches},
                    }
                )
        if len(case.gold) > 1 and case_errors:
            error_counts["MULTI_MENTION_COLLISION"] += 1
            case_errors.add("MULTI_MENTION_COLLISION")
        if case_errors:
            cases_with_errors += 1
        case_classifications.append(
            {
                "case_id": case.case_id,
                "mention_count": len(case.gold),
                "error_types": sorted(case_errors),
            }
        )
        for left in sorted(case_errors):
            for right in sorted(case_errors):
                if left < right:
                    cooccurrences[f"{left}+{right}"] += 1

    return {
        "provider": getattr(adapter, "provider", type(adapter).__name__),
        "detection": {
            "mode": "gold_span_queries",
            "measured": False,
            "errors": 0,
            "note": "Mention boundaries are fixed by the corpus; this report isolates composition."
        },
        "composition": {
            "mention_total": mention_total,
            "mention_exact_match": exact_total / mention_total if mention_total else 0.0,
            "cases_total": cases_total,
            "cases_with_errors": cases_with_errors,
            "error_counts": dict(error_counts),
            "cooccurrences": dict(cooccurrences),
            "case_classifications": case_classifications,
            "details": details,
        },
    }


def _error_type(field: str) -> str:
    return {
        "negated": "NEGATION_SCOPE",
        "temporality": "TEMPORAL_SCOPE",
        "experiencer": "FAMILY_EXPERIENCER_SCOPE",
        "dose": "DOSE_ATTACHMENT",
        "dose_value": "DOSE_ATTACHMENT",
        "dose_unit": "DOSE_ATTACHMENT",
        "frequency": "DOSE_ATTACHMENT",
        "route": "DOSE_ATTACHMENT",
        "laterality": "LATERALITY_ATTACHMENT",
        "status": "STATUS_CONFLICT",
    }.get(field, "ATTRIBUTE_MISBOUND")
