"""Generate a small review-only V6 quota-completion batch."""
from __future__ import annotations

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
from .models import ConversationSegment
from .review_queue import load_candidate_records
from .simulator import CandidateCase, write_candidates


ROOT = Path(__file__).parent
CORPORA = (
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    CONTEXT_VALIDATION_V6_DRAFT_PATH,
)
PREVIOUS_CANDIDATE_FILES = (
    ROOT / "results" / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl",
    ROOT / "results" / "clinical-language-simulator-v6-expansion-2026-08-15.jsonl",
)
DEFAULT_OUTPUT = ROOT / "results" / "clinical-language-simulator-v6-micro-expansion-2026-08-15.jsonl"


def main() -> None:
    official_texts = {
        case.text
        for path in CORPORA
        for case in load_corpus(path)
    }
    previous_records = tuple(
        record
        for path in PREVIOUS_CANDIDATE_FILES
        for record in load_candidate_records(path)
    )
    previous_texts = {str(record["text"]) for record in previous_records}
    excluded_texts = official_texts | previous_texts
    scenarios = (
        ("Você ainda usa enalapril?", "Parei no mês passado.", "status medication carry-over"),
        ("Alguém da família tem diabetes?", "Minha irmã tem.", "family experiencer carry-over"),
        ("A dor voltou?", "Só do lado esquerdo agora.", "laterality carry-over"),
        ("Qual dose da metformina?", "Aumentei para 850 mg ontem.", "dose carry-over"),
    )
    candidates: list[CandidateCase] = []
    for offset, (question, answer, gap) in enumerate(scenarios, 55):
        candidate_id = f"sim-v6-{offset:04d}"
        text = f"Médico: {question}\nPaciente: {answer}"
        if text in excluded_texts:
            raise RuntimeError(f"micro candidate overlaps an existing corpus: {candidate_id}")
        segment_01 = f"{candidate_id}:segment-01"
        segment_02 = f"{candidate_id}:segment-02"
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        candidates.append(
            CandidateCase(
                candidate_id=candidate_id,
                text=text,
                language="pt-BR",
                source_case_ids=(f"v6-micro-cross-segment-{offset - 54:03d}",),
                source_error_types=("CROSS_SEGMENT_RESOLUTION",),
                generator="deterministic-clinical-language-simulator-micro-expansion",
                provenance={
                    "source_corpus": "v6-micro-expansion-gap-analysis",
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
    output = DEFAULT_OUTPUT
    write_candidates(output, candidates)
    print(json.dumps({
        "status": "candidate-only",
        "candidate_count": len(candidates),
        "first_candidate_id": candidates[0].candidate_id,
        "last_candidate_id": candidates[-1].candidate_id,
        "all_pending": all(candidate.review_status == "PENDING_REVIEW" for candidate in candidates),
        "all_gold_null": all(candidate.gold is None for candidate in candidates),
        "official_corpus_mutation": False,
        "output": str(output),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
