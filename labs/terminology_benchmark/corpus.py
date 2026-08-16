"""Versioned, hand-reviewed PT-BR terminology benchmark corpus."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation


CORPUS_PATH = Path(__file__).with_name("data") / "pt_br_terminology_v1.jsonl"
CONTEXT_HARDENING_CORPUS_PATH = (
    Path(__file__).with_name("data") / "pt_br_clinical_semantics_v2.jsonl"
)
CONTEXT_VALIDATION_V3_PATH = (
    Path(__file__).with_name("data") / "pt_br_clinical_semantics_v3.jsonl"
)
CONTEXT_VALIDATION_V4_PATH = (
    Path(__file__).with_name("data") / "pt_br_clinical_semantics_v4.jsonl"
)
CONTEXT_VALIDATION_V5_PATH = (
    Path(__file__).with_name("data") / "pt_br_clinical_semantics_v5.jsonl"
)
CONTEXT_VALIDATION_V6_DRAFT_PATH = (
    Path(__file__).with_name("data") / "pt_br_clinical_semantics_v6_draft.jsonl"
)
CONTEXT_VALIDATION_V6_PATH = (
    Path(__file__).with_name("data") / "pt_br_clinical_semantics_v6.jsonl"
)


def load_corpus(path: Path = CORPUS_PATH) -> tuple[BenchmarkCase, ...]:
    cases: list[BenchmarkCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        payload = json.loads(line)
        segments = tuple(
            ConversationSegment(
                segment_id=segment["segment_id"],
                speaker=segment["speaker"],
                text=segment["text"],
            )
            for segment in payload.get("segments", ())
        )
        cases.append(
            BenchmarkCase(
                case_id=payload["case_id"],
                text=payload["text"],
                language=payload.get("language", "pt-BR"),
                source=payload.get("source", "niede-pt-br-v1"),
                segments=segments,
                gold=tuple(
                    GoldMention(
                        **{
                            **item,
                            "relations": tuple(
                                GoldRelation(**relation)
                                for relation in item.get("relations", ())
                            ),
                            "segment_ids": tuple(item.get("segment_ids", ())),
                            "attribute_provenance": {
                                key: tuple(value)
                                for key, value in item.get("attribute_provenance", {}).items()
                            },
                            "relation_provenance": {
                                key: tuple(value)
                                for key, value in item.get("relation_provenance", {}).items()
                            },
                        }
                    )
                    for item in payload["gold"]
                ),
            )
        )
    return tuple(cases)


def mention_span(text: str, surface: str, occurrence: int = 0) -> tuple[int, int]:
    """Return a gold span and fail loudly when the corpus is malformed."""
    folded = text.casefold()
    needle = surface.casefold()
    matches = list(re.finditer(re.escape(needle), folded))
    boundary_matches = [
        match
        for match in matches
        if _has_surface_boundaries(folded, match.start(), match.end(), needle)
    ]
    selected = boundary_matches or matches
    if occurrence >= len(selected):
        raise ValueError(f"surface {surface!r} is not present enough times in {text!r}")
    match = selected[occurrence]
    return match.start(), match.end()


def _has_surface_boundaries(text: str, start: int, end: int, surface: str) -> bool:
    if surface and surface[0].isalnum() and start > 0 and text[start - 1].isalnum():
        return False
    if surface and surface[-1].isalnum() and end < len(text) and text[end].isalnum():
        return False
    return True


def benchmark_target_terms(cases: tuple[BenchmarkCase, ...] | None = None) -> tuple[str, ...]:
    """Return gold mention surfaces for the context-only target matcher."""
    selected = cases or load_corpus()
    return tuple(
        dict.fromkeys(
            gold.surface
            for case in selected
            for gold in case.gold
        )
    )
