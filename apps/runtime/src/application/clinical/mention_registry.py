"""Stable registry for normalized mentions across streaming revisions."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from packages.clinical_facts_sdk import ClinicalMention


@dataclass(frozen=True, slots=True)
class RegisteredMention:
    mention: ClinicalMention
    lifecycle: str
    update_count: int


class MentionRegistry:
    """Merge repeated transcript observations into one clinical mention."""

    def __init__(self) -> None:
        self._mentions: dict[str, ClinicalMention] = {}
        self._keys: dict[tuple[str, str, str, str, str], str] = {}
        self._counts: dict[str, int] = {}

    @property
    def mentions(self) -> tuple[ClinicalMention, ...]:
        return tuple(self._mentions.values())

    def upsert(
        self,
        mention: ClinicalMention,
        *,
        encounter_id: str,
        subject_id: str,
    ) -> RegisteredMention:
        concept = (mention.code or mention.concept_id or mention.normalized_text).casefold()
        key = (
            encounter_id,
            subject_id,
            concept,
            "negative" if mention.negated else "positive",
            mention.temporality.casefold(),
        )
        stable_id = self._keys.get(key)
        if stable_id is None:
            stable_id = "mention-" + sha256("|".join(key).encode("utf-8")).hexdigest()[:20]
            registered = replace(
                mention,
                id=stable_id,
                provenance={
                    **dict(mention.provenance),
                    "registry_key": stable_id,
                    "observations": (mention.id,),
                },
            )
            self._keys[key] = stable_id
            self._mentions[stable_id] = registered
            self._counts[stable_id] = 1
            return RegisteredMention(registered, "created", 1)

        previous = self._mentions[stable_id]
        observations = tuple(dict.fromkeys((
            *previous.provenance.get("observations", ()),
            mention.id,
        )))
        provenance: dict[str, Any] = {
            **dict(previous.provenance),
            **dict(mention.provenance),
            "registry_key": stable_id,
            "observations": observations,
            "source_segments": tuple(dict.fromkeys((
                *previous.provenance.get("source_segments", ()),
                previous.segment_id,
            ))),
        }
        registered = replace(
            previous,
            original_text=mention.original_text,
            normalized_text=mention.normalized_text,
            confidence=max(previous.confidence, mention.confidence),
            certainty=mention.certainty,
            status=mention.status,
            negated=mention.negated,
            reported=mention.reported,
            speaker=mention.speaker,
            provenance={key: value for key, value in provenance.items() if value is not None},
            segment_id=mention.segment_id or previous.segment_id,
            revision=max(previous.revision, mention.revision),
            review_required=previous.review_required or mention.review_required,
            ontology=mention.ontology or previous.ontology,
            code=mention.code or previous.code,
            semantic_value=mention.semantic_value if mention.semantic_value is not None else previous.semantic_value,
            semantic_unit=mention.semantic_unit or previous.semantic_unit,
            segment_before=mention.segment_before or previous.segment_before,
            segment_current=mention.segment_current or previous.segment_current,
            segment_after=mention.segment_after or previous.segment_after,
            updated_at=datetime.now(timezone.utc),
        )
        self._mentions[stable_id] = registered
        self._counts[stable_id] = self._counts.get(stable_id, 1) + 1
        return RegisteredMention(registered, "growing", self._counts[stable_id])
