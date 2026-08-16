"""Deterministic projection normalization for canonical transcript documents."""
from __future__ import annotations

import re

from .models import Transcript, TranscriptSegment


class TranscriptNormalizer:
    """Normalize obvious ASR variants while preserving original evidence."""

    def normalize(self, transcript: Transcript) -> Transcript:
        normalized_segments: list[TranscriptSegment] = []
        for segment in transcript.segments:
            normalized = self._normalize_text(segment.text)
            normalized_segments.append(
                segment
                if normalized == segment.text
                else TranscriptSegment(
                    segment_id=segment.segment_id,
                    text=normalized,
                    raw_text=segment.raw_text or segment.text,
                    projected_text=segment.projected_text,
                    projected_text_clean=segment.projected_text_clean,
                    start_ms=segment.start_ms,
                    end_ms=segment.end_ms,
                    sequence=segment.sequence,
                    revision=segment.revision,
                    confidence=segment.confidence,
                    speaker=segment.speaker,
                    words=segment.words,
                )
            )
        return Transcript(
            request_id=transcript.request_id,
            language=transcript.language,
            provider=transcript.provider,
            segments=tuple(normalized_segments),
        )

    @staticmethod
    def _normalize_text(text: str) -> str:
        normalized = text
        replacements = (
            (r"cans[áa]cio", "cansaço"),
            (r"na\s+[áa]usia", "náusea"),
            (r"n[aã]o\s+vou\s+me\s+ter", "não vomitei"),
            (r"embassada", "embaçada"),
            (r"loss\s+artana", "losartana"),
        )
        for pattern, replacement in replacements:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        return re.sub(r"(\d+)\s*mg\b", r"\1 mg", normalized, flags=re.IGNORECASE)
