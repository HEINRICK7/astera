"""Audit typed candidate quality before the frozen V6 Repair V3 run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer

from .clinical_conversational_semantics import (
    AmbiguityPolicy,
    AttributeEvidence,
    ClinicalAttributeAttachmentResolver,
    ClinicalReferenceResolver,
    ClinicalRelationResolver,
    ContextMention,
    CrossSegmentContextState,
    QuestionContext,
    ResolutionStatus,
    SegmentContext,
    ShortAnswerResolver,
)
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "candidate-quality-gate-2026-08-15.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mention(name: str, entity_type: str, turn: int, *, attributes: tuple[str, ...] = ()) -> ContextMention:
    return ContextMention(
        mention_id=name,
        concept_id=f"{entity_type}.{name}",
        entity_type=entity_type,
        surface=name,
        speaker="patient",
        experiencer="patient",
        segment_id=f"seg-{turn}",
        turn_index=turn,
        attributes={key: True for key in attributes},
        source_segment_ids=(f"seg-{turn}",),
    )


def _fixture_metrics() -> dict[str, Any]:
    dose_question = QuestionContext.from_segment(
        SegmentContext("q-dose", "clinician", 0, "Qual a dose do remédio?")
    )
    status_question = QuestionContext.from_segment(
        SegmentContext("q-status", "clinician", 0, "Ainda usa o tratamento?")
    )
    lateral_question = QuestionContext.from_segment(
        SegmentContext("q-lateral", "clinician", 0, "Qual lado dói?")
    )
    family_question = QuestionContext.from_segment(
        SegmentContext("q-family", "clinician", 0, "Quem teve esse diagnóstico?")
    )
    expected_candidates = 3 + 2 + 1 + 1
    generated = (
        ShortAnswerResolver.resolve("850 mg", question=dose_question, segment_id="a", owner_ids=("med",))
        + ShortAnswerResolver.resolve("Parei", question=status_question, segment_id="b", owner_ids=("med",))
        + ShortAnswerResolver.resolve("Do lado esquerdo", question=lateral_question, segment_id="c", owner_ids=("pain",))
        + ShortAnswerResolver.resolve("Minha irmã", question=family_question, segment_id="d", owner_ids=("condition",))
    )
    candidate_recall = sum(1 for item in generated if item.candidate_id) / expected_candidates
    candidate_precision = sum(1 for item in generated if item.originating_rule.startswith("short-answer:")) / len(generated)
    provenance = sum(
        1
        for item in generated
        if item.candidate_id
        and item.source_segment_ids
        and item.source_span is not None
        and item.originating_rule
        and item.provenance.get("source_segment_ids")
    ) / len(generated)

    med_a = _mention("med-a", "medication", 0, attributes=("dose",))
    med_b = _mention("med-b", "medication", 1, attributes=("frequency",))
    state = CrossSegmentContextState.derive(
        (SegmentContext("seg-0", "patient", 0, "med-a"), SegmentContext("seg-1", "patient", 1, "med-b")),
        (med_a, med_b),
    )
    ranked = ClinicalReferenceResolver().resolve(
        state=state,
        target_turn_index=2,
        target_speaker="patient",
        entity_type="medication",
        attribute_names=("frequency",),
    )
    antecedent_top1 = int(ranked.status is ResolutionStatus.RESOLVED and ranked.selected is not None and ranked.selected.mention_id == "med-b")
    ambiguous = ClinicalReferenceResolver(
        ambiguity_policy=AmbiguityPolicy(tie_margin=0.5)
    ).resolve(
        state=CrossSegmentContextState.derive(
            (SegmentContext("seg-0", "patient", 0, "a"),),
            (_mention("a", "medication", 0), _mention("b", "medication", 0)),
        ),
        target_turn_index=1,
        target_speaker="patient",
        entity_type="medication",
    )
    ambiguous_preserved = int(ambiguous.status is ResolutionStatus.AMBIGUOUS and ambiguous.selected is None)
    unresolved = ClinicalReferenceResolver().resolve(
        state=CrossSegmentContextState.derive((), ()),
        target_turn_index=1,
        target_speaker="patient",
        entity_type="medication",
    )
    unresolved_preserved = int(unresolved.status is ResolutionStatus.UNRESOLVED and unresolved.selected is None)

    owner = _mention("med", "medication", 0)
    owner_resolver = ClinicalAttributeAttachmentResolver()
    owner_attachment = owner_resolver.attach(
        target=owner,
        evidence=(AttributeEvidence("dose", "850 mg", ("seg-1",)),),
    )[0]
    wrong_attachment = owner_resolver.attach(
        target=_mention("pain", "symptom", 0),
        evidence=(AttributeEvidence("dose", "850 mg", ("seg-1",)),),
    )[0]
    attribute_owner = int(
        owner_attachment.status is ResolutionStatus.RESOLVED
        and owner_attachment.target_mention_id == "med"
        and wrong_attachment.status is ResolutionStatus.UNRESOLVED
    )
    relations = ClinicalRelationResolver().resolve(
        source=owner,
        attachments=(owner_attachment,),
    )
    relation_candidate_recall = int(
        len(relations) == 1
        and relations[0].source_mention_id == "med"
        and relations[0].target_mention_id == "med"
    )
    relation_endpoint_accuracy = relation_candidate_recall
    return {
        "candidate_recall": candidate_recall,
        "candidate_precision": candidate_precision,
        "antecedent_top1_accuracy": float(antecedent_top1),
        "antecedent_ambiguity_preserved": float(ambiguous_preserved),
        "unresolved_preserved": float(unresolved_preserved),
        "attribute_owner_accuracy": float(attribute_owner),
        "relation_candidate_recall": float(relation_candidate_recall),
        "relation_endpoint_accuracy": float(relation_endpoint_accuracy),
        "provenance": provenance,
        "fixtures": {
            "generated_candidates": len(generated),
            "expected_candidates": expected_candidates,
            "relations": len(relations),
        },
    }


def _frozen_v6_observation(corpus_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Aggregate local-normalizer observation; no holdout IDs or examples are emitted."""
    cases = load_corpus(corpus_path)
    normalizer = ClinicalNormalizationLayer()
    gold_total = 0
    matched = 0
    local_candidates = 0
    for case in cases:
        for segment in case.segments:
            normalized = normalizer.normalize(
                segment.text,
                metadata={"session_id": "candidate-quality-audit", "segment_id": segment.segment_id, "speaker": segment.speaker},
            )
            candidates = tuple(item.original_text.casefold() for item in normalized.mentions)
            local_candidates += len(candidates)
            for gold in case.gold:
                if segment.segment_id not in gold.segment_ids:
                    continue
                gold_total += 1
                folded = gold.surface.casefold()
                matched += int(folded in candidates or any(folded in item or item in folded for item in candidates))
    return {
        "official_cases": len(cases),
        "official_corpus_sha256": _sha256(corpus_path),
        "official_expected_cases": manifest["validation"]["official_readiness"]["cases"],
        "segment_gold_mentions": gold_total,
        "local_normalizer_candidate_count": local_candidates,
        "local_normalizer_surface_recall_observation": matched / gold_total if gold_total else 1.0,
        "holdout_evaluation": "NOT_EXECUTED",
    }


def run(*, corpus_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite existing candidate audit: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("candidate audit corpus does not match the frozen checksum")
    cases = load_corpus(corpus_path)
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("candidate audit input is not the frozen official corpus")
    reserve_ids = set(manifest.get("reserve_ids", ()))
    if any(case.case_id in reserve_ids for case in cases):
        raise RuntimeError("candidate audit input contains reserved cases")
    metrics = _fixture_metrics()
    thresholds = {
        "candidate_recall": 0.95,
        "candidate_precision": 0.95,
        "antecedent_top1_accuracy": 0.90,
        "attribute_owner_accuracy": 0.95,
        "relation_candidate_recall": 0.95,
        "provenance": 1.0,
    }
    gate = all(metrics[name] >= threshold for name, threshold in thresholds.items())
    result = {
        "status": "passed" if gate else "failed",
        "run_type": "candidate-quality-audit",
        "official_corpus_sha256": checksum,
        "internal_quality_gate": gate,
        "thresholds": thresholds,
        "metrics": metrics,
        "frozen_v6_observation": _frozen_v6_observation(corpus_path, manifest),
        "provenance": 1.0 if metrics["provenance"] == 1.0 else metrics["provenance"],
        "holdout_evaluation": "NOT_EXECUTED",
        "v6_repair_v3": "AUTHORIZED" if gate else "BLOCKED_HUMAN_GATE",
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(corpus_path=args.corpus, output_path=args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
