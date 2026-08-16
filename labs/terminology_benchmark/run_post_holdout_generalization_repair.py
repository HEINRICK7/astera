"""Run the internal gate for the post-holdout generalization repair.

The fixtures here are engineering cases only. They are distinct from the
consumed V6 holdouts and are not the subsequent unseen holdout-v2 set.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_harness import _actual_relations, _expected_relations
from .context_safety import NieDEPtBrSafetyRules
from .cross_segment_context import CrossSegmentContextAdapter
from .models import BenchmarkCase, ConversationSegment, GoldMention


OUTPUT = Path(__file__).parent / "results/post-holdout-generalization-repair-internal-gate-2026-08-15.json"


def _case(case_id: str, question: str, answer: str, gold: dict[str, Any]) -> BenchmarkCase:
    return BenchmarkCase(
        case_id=case_id,
        text=f"Médico: {question}\nPaciente: {answer}",
        language="pt-BR",
        source="post-holdout-engineering",
        segments=(
            ConversationSegment(f"{case_id}:q", "clinician", question),
            ConversationSegment(f"{case_id}:a", "patient", answer),
        ),
        gold=(GoldMention(**gold),),
    )


INTERNAL_CASES = (
    _case(
        "post-repair-gate-laterality",
        "Onde sente o formigamento?",
        "Agora está apenas no braço esquerdo.",
        {"surface": "formigamento", "concept_id": "symptom.tingling", "laterality": "left"},
    ),
    _case(
        "post-repair-gate-dose",
        "Qual dose da dipirona?",
        "Passei para 1 g hoje.",
        {"surface": "dipirona", "concept_id": "medication.dipyrone", "dose": "1 g", "dose_value": "1", "dose_unit": "g", "status": "active"},
    ),
    _case(
        "post-repair-gate-temporality",
        "Como está a dose da levotiroxina?",
        "Reduzi para 88 mcg na semana passada.",
        {"surface": "levotiroxina", "concept_id": "medication.levothyroxine", "temporality": "current", "dose": "88 mcg", "dose_value": "88", "dose_unit": "mcg", "status": "active"},
    ),
    _case(
        "post-repair-gate-family",
        "Quem tem asma na família?",
        "Minha mãe tem.",
        {"surface": "asma", "concept_id": "condition.asthma", "experiencer": "family"},
    ),
)


def _provenance_ok(result: Any, case: BenchmarkCase) -> bool:
    provenance = result.provenance
    known = {segment.segment_id for segment in case.segments}
    return bool(
        provenance.get("provider")
        and provenance.get("source_text") == case.text
        and provenance.get("source_scope") == "conversation"
        and set(provenance.get("conversation_segment_ids", ())).issubset(known)
        and all(
            set(sources).issubset(known)
            for sources in provenance.get("segment_provenance", {}).values()
        )
    )


async def run() -> dict[str, Any]:
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), INTERNAL_CASES)
    records: list[dict[str, Any]] = []
    relation_passes = 0
    relation_total = 0
    temporal_passes = 0
    temporal_total = 0
    provenance_passes = 0
    provenance_total = 0
    for case in INTERNAL_CASES:
        gold = case.gold[0]
        start = case.text.index(gold.surface)
        result = await adapter.analyze(ClinicalContextQuery(
            text=case.text,
            language=case.language,
            start=start,
            end=start + len(gold.surface),
            evidence_id=case.case_id,
            semantic_policy="clinical-semantic-policy-v1.2",
        ))
        expected_relations = _expected_relations(gold)
        actual_relations = _actual_relations(result)
        if expected_relations:
            relation_total += 1
            relation_passes += int(actual_relations == expected_relations)
        if gold.temporality == "current" and any(word in case.segments[1].text.casefold() for word in ("ontem", "semana passada")):
            temporal_total += 1
            temporal_passes += int(
                result.temporality == "current"
                and result.provenance.get("event_temporality", {}).get("owner") == "dose_change_event"
            )
        provenance_total += 1
        provenance_passes += int(_provenance_ok(result, case))
        records.append({
            "case_id": case.case_id,
            "mention": gold.surface,
            "fields": {
                field: {"expected": getattr(gold, field), "actual": getattr(result, field), "match": getattr(gold, field) == getattr(result, field)}
                for field in ("temporality", "experiencer", "laterality", "dose", "dose_value", "dose_unit", "status")
            },
            "relations_expected": expected_relations,
            "relations_actual": actual_relations,
            "provenance_contract": _provenance_ok(result, case),
            "event_temporality": result.provenance.get("event_temporality"),
        })
    metrics = {
        "relation_materialization_rate": relation_passes / relation_total if relation_total else 1.0,
        "temporal_ownership_accuracy": temporal_passes / temporal_total if temporal_total else 1.0,
        "provenance_contract_rate": provenance_passes / provenance_total if provenance_total else 1.0,
    }
    report = {
        "status": "PASS" if all(value == 1.0 for value in metrics.values()) else "FAIL",
        "repair": "post-holdout-generalization-repair",
        "fixtures": "engineering-only; not consumed holdouts and not holdout-v2",
        "old_holdouts_used": False,
        "metrics": metrics,
        "gate_thresholds": {key: 1.0 for key in metrics},
        "cases": records,
        "resolver_policy_corpus_changed": {"resolver": True, "policy": False, "corpus": False},
        "old_holdouts": {"consumed": True, "rerun": False, "used_for_approval": False},
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    print(json.dumps(asyncio.run(run()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
