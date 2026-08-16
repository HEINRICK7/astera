"""Generate the next review-only V6 simulator batch."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .corpus import (
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    CONTEXT_VALIDATION_V6_DRAFT_PATH,
    load_corpus,
)
from .review_queue import load_candidate_records
from .models import ConversationSegment
from .simulator import CandidateCase, ClinicalLanguageSimulator, load_failure_seeds, write_candidates


ROOT = Path(__file__).parent
TAXONOMIES = tuple(ROOT / "results" / f"context-taxonomy-v{version}-2026-08-15.json" for version in (3, 4, 5))
CORPORA = (
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    CONTEXT_VALIDATION_V6_DRAFT_PATH,
)
HISTORICAL_MANIFEST = ROOT / "data" / "historical_failure_manifest.json"
EXISTING_CANDIDATES = ROOT / "results" / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl"
DEFAULT_OUTPUT = ROOT / "results" / "clinical-language-simulator-v6-expansion-2026-08-15.jsonl"


def _cross_segment_candidates(start: int, excluded_texts: set[str]) -> tuple[CandidateCase, ...]:
    scenarios = (
        ("Continua usando losartana?", "Não, parei na semana passada.", "medication carry-over"),
        ("Sua mãe teve câncer?", "Teve, de mama.", "family experiencer carry-over"),
        ("A dor melhorou?", "Sim, não sinto mais, só formigamento na mão direita.", "multi-turn negation"),
        ("Ainda usa a bombinha?", "Só quando tem chiado.", "medication context carry-over"),
        ("O pai teve AVC?", "Teve aos 60.", "family temporal carry-over"),
        ("Está tomando metformina?", "Passei de 500 para 850 depois do jantar.", "dose carry-over"),
    )
    candidates: list[CandidateCase] = []
    for ordinal, (question, answer, gap) in enumerate(scenarios):
        segment_01 = f"sim-v6-{start + ordinal:04d}:segment-01"
        segment_02 = f"sim-v6-{start + ordinal:04d}:segment-02"
        text = f"Médico: {question}\nPaciente: {answer}"
        if text in excluded_texts:
            raise RuntimeError(f"cross-segment candidate overlaps an existing text: {text}")
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        candidates.append(
            CandidateCase(
                candidate_id=f"sim-v6-{start + ordinal:04d}",
                text=text,
                language="pt-BR",
                source_case_ids=(f"v6-cross-segment-{ordinal + 1:03d}",),
                source_error_types=("CROSS_SEGMENT_RESOLUTION",),
                generator="deterministic-clinical-language-simulator-cross-segment",
                provenance={
                    "source_corpus": "v6-cross-segment-gap-analysis",
                    "history_status": gap,
                    "candidate_text_sha256": text_hash,
                    "official_corpus_mutation": False,
                },
                segments=(
                    ConversationSegment(segment_01, "clinician", question),
                    ConversationSegment(segment_02, "patient", answer),
                ),
            )
        )
    return tuple(candidates)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--per-error-type", type=int, default=6)
    parser.add_argument("--limit", type=int, default=34)
    parser.add_argument("--minimum", type=int, default=34)
    args = parser.parse_args()
    if args.limit < args.minimum:
        raise ValueError("limit must be at least minimum")

    seeds = load_failure_seeds(CORPORA[:3], TAXONOMIES, HISTORICAL_MANIFEST)
    official_cases = tuple(case for path in CORPORA for case in load_corpus(path))
    existing_records = load_candidate_records(EXISTING_CANDIDATES)
    existing_texts = {str(record["text"]) for record in existing_records}
    candidates = ClinicalLanguageSimulator().generate(
        seeds,
        official_cases,
        per_error_type=args.per_error_type,
        limit=args.limit,
        excluded_texts=existing_texts,
        candidate_id_start=15,
    )
    if len(candidates) < args.minimum:
        raise RuntimeError(f"expansion generated only {len(candidates)} candidates; minimum is {args.minimum}")
    excluded_texts = existing_texts | {candidate.text for candidate in candidates}
    cross_candidates = _cross_segment_candidates(15 + len(candidates), excluded_texts)
    candidates = tuple(candidates) + cross_candidates
    if any(candidate.gold is not None or candidate.review_status != "PENDING_REVIEW" for candidate in candidates):
        raise RuntimeError("expansion candidates must remain gold-free and PENDING_REVIEW")
    write_candidates(args.output, candidates)
    print(
        json.dumps(
            {
                "status": "candidate-only",
                "candidate_count": len(candidates),
                "first_candidate_id": candidates[0].candidate_id,
                "last_candidate_id": candidates[-1].candidate_id,
                "cross_segment_candidates": len(cross_candidates),
                "excluded_corpora": [path.stem for path in CORPORA],
                "excluded_existing_candidates": len(existing_texts),
                "official_corpus_mutation": False,
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
