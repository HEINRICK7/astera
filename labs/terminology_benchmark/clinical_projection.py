"""Internal relational projection used by context repair experiments."""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ClinicalRelation:
    relation_type: str
    source: str
    target: str
    value: str
    provenance: Mapping[str, Any]
    relation_id: str | None = None
    source_mention_id: str | None = None
    target_mention_id: str | None = None
    source_segment_ids: tuple[str, ...] = ()
    confidence: float = 1.0


@dataclass(frozen=True, slots=True)
class ClinicalRelationSet:
    """Immutable final relation graph emitted by the compiler only."""

    relations: tuple[ClinicalRelation, ...] = ()

    def __post_init__(self) -> None:
        immutable_relations = tuple(
            ClinicalRelation(
                relation_type=item.relation_type,
                source=item.source,
                target=item.target,
                value=item.value,
                provenance=MappingProxyType(dict(item.provenance)),
                relation_id=item.relation_id,
                source_mention_id=item.source_mention_id,
                target_mention_id=item.target_mention_id,
                source_segment_ids=tuple(item.source_segment_ids),
                confidence=item.confidence,
            )
            for item in self.relations
        )
        object.__setattr__(self, "relations", immutable_relations)
        keys = [
            (item.relation_type, item.source, item.target, str(item.value))
            for item in immutable_relations
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("final clinical relation set contains duplicate relations")

    def __iter__(self):
        return iter(self.relations)


class ClinicalRelationCompiler:
    """Compile resolved semantic truth into one immutable relation set.

    This module deliberately does not resolve mentions or attributes. It only
    consumes resolved values, ownership, transitions and provenance. Callers
    may retain relation candidates as intermediate signals, but only this
    compiler creates the final relation set.
    """

    _DERIVED: dict[str, tuple[str, tuple[str, ...]]] = {
        "dose": ("HAS_DOSE", ("medication", "treatment")),
        "frequency": ("HAS_FREQUENCY", ("medication", "treatment")),
        "route": ("HAS_ROUTE", ("medication", "treatment")),
        "laterality": ("HAS_LATERALITY", ("symptom", "condition", "anatomical")),
    }
    _TRANSITION_TYPES = {"CHANGED_FROM", "CHANGED_TO", "REFERS_TO"}

    def compile(self, resolved: Any) -> ClinicalRelationSet:
        attributes = dict(resolved.resolved_attributes)
        provenance = resolved.provenance
        ownership = provenance.get("attribute_ownership", {})
        owner_type = provenance.get("owner_type")
        owner_id = provenance.get("owner_mention_id")
        owner_segments = tuple(provenance.get("source_segment_ids", ()))
        if resolved.resolved_mentions:
            mention = resolved.resolved_mentions[0]
            owner_id = owner_id or mention.mention_id
            owner_type = owner_type or mention.entity_type
            owner_segments = owner_segments or tuple(mention.source_segment_ids)

        relations: list[ClinicalRelation] = []
        seen: set[tuple[str, str, str, str]] = set()

        def add(relation: ClinicalRelation) -> None:
            key = (relation.relation_type, relation.source, relation.target, str(relation.value))
            if key not in seen:
                relations.append(relation)
                seen.add(key)

        def field_sources(field: str) -> tuple[str, ...]:
            explicit = ownership.get(field, {}) if isinstance(ownership, Mapping) else {}
            if isinstance(explicit, Mapping) and explicit.get("source_segment_ids"):
                return tuple(explicit["source_segment_ids"])
            for key in ("attribute_provenance", "segment_provenance"):
                source_map = provenance.get(key, {})
                if isinstance(source_map, Mapping) and source_map.get(field):
                    return tuple(source_map[field])
            legacy = provenance.get(field, ())
            return tuple(legacy) or owner_segments

        def field_owner(field: str) -> tuple[str | None, str | None]:
            explicit = ownership.get(field, {}) if isinstance(ownership, Mapping) else {}
            if isinstance(explicit, Mapping):
                return explicit.get("owner_type", owner_type), explicit.get("owner_mention_id", owner_id)
            return owner_type, owner_id

        # Existing relations are signals only. Derived relations are rebuilt
        # from current resolved attributes so stale local values cannot survive.
        signals = list(getattr(resolved, "resolved_relations", ()) or ())
        signals.extend(_relation_from_dict(item) for item in provenance.get("transition_evidence", ()))
        signals.extend(_relation_from_dict(item) for item in provenance.get("relation_signals", ()))
        derived_types = {item[0] for item in self._DERIVED.values()} | {"DISCONTINUED_AT"}
        for signal in signals:
            if signal.relation_type in self._TRANSITION_TYPES:
                transition_source = owner_id if signal.relation_type != "REFERS_TO" and owner_id else signal.source
                transition_provenance = dict(signal.provenance)
                transition_provenance.setdefault("rule", "clinical-relation-compiler-v1")
                add(ClinicalRelation(
                    relation_type=signal.relation_type,
                    source=str(transition_source),
                    target=signal.target,
                    value=signal.value,
                    provenance=transition_provenance,
                    relation_id=signal.relation_id or f"{transition_source}:{signal.relation_type}:{signal.target}:{signal.value}",
                    source_mention_id=str(transition_source),
                    target_mention_id=signal.target_mention_id,
                    source_segment_ids=signal.source_segment_ids,
                    confidence=signal.confidence,
                ))
            elif signal.relation_type in derived_types and not owner_id:
                # Backward-compatible resolved intent: without an ownership
                # record there is no safe way to reconstruct its source.
                add(signal)
            elif signal.relation_type not in derived_types:
                # Non-derived resolved relation intents (for example REFERS_TO
                # variants or future vocabulary) remain compiler-owned but are
                # not re-inferred here.
                add(signal)

        for field, (relation_type, owner_types) in self._DERIVED.items():
            value = attributes.get(field)
            resolved_owner_type, resolved_owner_id = field_owner(field)
            if value is None or resolved_owner_type not in owner_types or not resolved_owner_id:
                continue
            source_segments = field_sources(field)
            add(ClinicalRelation(
                relation_type=relation_type,
                source=str(resolved_owner_id),
                target=field,
                value=str(value),
                provenance={
                    "rule": "clinical-relation-compiler-v1",
                    "attribute": field,
                    "source_segment_ids": source_segments,
                },
                relation_id=f"{resolved_owner_id}:{relation_type}:{field}",
                source_mention_id=str(resolved_owner_id),
                target_mention_id=field,
                source_segment_ids=source_segments,
            ))

        if attributes.get("status") == "discontinued":
            resolved_owner_type, resolved_owner_id = field_owner("status")
            if resolved_owner_type in {"medication", "treatment"} and resolved_owner_id:
                source_segments = field_sources("status")
                add(ClinicalRelation(
                    relation_type="DISCONTINUED_AT",
                    source=str(resolved_owner_id),
                    target="status",
                    value="discontinued",
                    provenance={
                        "rule": "clinical-relation-compiler-v1",
                        "event": "discontinued",
                        "source_segment_ids": source_segments,
                    },
                    relation_id=f"{resolved_owner_id}:DISCONTINUED_AT:status",
                    source_mention_id=str(resolved_owner_id),
                    target_mention_id="status",
                    source_segment_ids=source_segments,
                ))
        return ClinicalRelationSet(tuple(relations))


def _relation_from_dict(item: Any) -> ClinicalRelation:
    if isinstance(item, ClinicalRelation):
        return item
    return ClinicalRelation(
        relation_type=str(item.get("relation_type", "")),
        source=str(item.get("source", "")),
        target=str(item.get("target", "")),
        value=str(item.get("value", "")),
        provenance=item.get("provenance", {}),
        relation_id=item.get("relation_id"),
        source_mention_id=item.get("source_mention_id"),
        target_mention_id=item.get("target_mention_id"),
        source_segment_ids=tuple(item.get("source_segment_ids", ())),
        confidence=float(item.get("confidence", 1.0)),
    )


@dataclass(frozen=True, slots=True)
class ClinicalMentionProjection:
    mention_id: str
    concept: str | None
    attributes: Mapping[str, Any]
    relations: tuple[ClinicalRelation, ...]

    def to_provenance(self) -> dict[str, Any]:
        return {
            "mention_id": self.mention_id,
            "attributes": dict(self.attributes),
            "relations": [
                {
                    "relation_id": relation.relation_id,
                    "relation_type": relation.relation_type,
                    "source": relation.source,
                    "target": relation.target,
                    "value": relation.value,
                    "source_mention_id": relation.source_mention_id or relation.source,
                    "target_mention_id": relation.target_mention_id or relation.target,
                    "source_segment_ids": list(relation.source_segment_ids),
                    "confidence": relation.confidence,
                    "provenance": dict(relation.provenance),
                }
                for relation in self.relations
            ],
        }


class ClinicalRelationMaterializer:
    """Legacy compatibility helper; not a production relation writer.

    Historical tests and callers may still use this API. The authoritative
    runtime path uses :class:`ClinicalRelationCompiler` instead, so this helper
    must not be introduced into new projection code.
    """

    _DERIVED: dict[str, tuple[str, tuple[str, ...]]] = {
        "dose": ("HAS_DOSE", ("medication", "treatment")),
        "frequency": ("HAS_FREQUENCY", ("medication", "treatment")),
        "route": ("HAS_ROUTE", ("medication", "treatment")),
        "laterality": ("HAS_LATERALITY", ("symptom", "condition", "anatomical")),
    }

    @classmethod
    def materialize(
        cls,
        *,
        source: str,
        owner_type: str | None,
        attributes: Mapping[str, Any],
        existing: tuple[ClinicalRelation, ...],
        attribute_sources: Mapping[str, tuple[str, ...] | list[str]] | None = None,
    ) -> tuple[ClinicalRelation, ...]:
        sources = attribute_sources or {}
        relation_to_field = {relation_type: field for field, (relation_type, _) in cls._DERIVED.items()}
        result: list[ClinicalRelation] = []
        seen: set[tuple[str, str, str]] = set()

        for relation in existing:
            field = relation_to_field.get(relation.relation_type)
            if field is not None:
                relation_type, owner_types = cls._DERIVED[field]
                current = attributes.get(field)
                if owner_type not in owner_types or current is None or str(current) != str(relation.value):
                    # A derived relation with an old value is not a current
                    # attribute relation. A valid CHANGED_FROM relation is a
                    # separate vocabulary entry and is intentionally retained.
                    continue
                source_segment_ids = tuple(sources.get(field, ())) or relation.source_segment_ids
                relation = ClinicalRelation(
                    relation_type=relation_type,
                    source=source,
                    target=field,
                    value=str(current),
                    provenance={
                        "rule": "resolved-attribute-materialization-v2",
                        "attribute": field,
                        "source_segment_ids": source_segment_ids,
                    },
                    relation_id=f"{source}:{relation_type}:{field}",
                    source_mention_id=source,
                    target_mention_id=field,
                    source_segment_ids=source_segment_ids,
                    confidence=relation.confidence,
                )
            if relation.relation_type == "DISCONTINUED_AT":
                if attributes.get("status") != "discontinued" or owner_type not in {"medication", "treatment"}:
                    continue
                source_segment_ids = tuple(sources.get("status", ())) or relation.source_segment_ids
                relation = ClinicalRelation(
                    relation_type=relation.relation_type,
                    source=source,
                    target="status",
                    value="discontinued",
                    provenance={
                        "rule": "resolved-discontinued-materialization-v2",
                        "source_segment_ids": source_segment_ids,
                    },
                    relation_id=f"{source}:DISCONTINUED_AT:status",
                    source_mention_id=source,
                    target_mention_id="status",
                    source_segment_ids=source_segment_ids,
                    confidence=relation.confidence,
                )
            key = (relation.relation_type, relation.target, str(relation.value))
            if key not in seen:
                result.append(relation)
                seen.add(key)

        for field, (relation_type, owner_types) in cls._DERIVED.items():
            value = attributes.get(field)
            if value is None or owner_type not in owner_types:
                continue
            key = (relation_type, field, str(value))
            if key in seen:
                continue
            source_segment_ids = tuple(sources.get(field, ())) or ()
            result.append(ClinicalRelation(
                relation_type=relation_type,
                source=source,
                target=field,
                value=str(value),
                provenance={
                    "rule": "resolved-attribute-materialization-v2",
                    "attribute": field,
                    "source_segment_ids": source_segment_ids,
                },
                relation_id=f"{source}:{relation_type}:{field}",
                source_mention_id=source,
                target_mention_id=field,
                source_segment_ids=source_segment_ids,
            ))
            seen.add(key)

        if attributes.get("status") == "discontinued" and owner_type in {"medication", "treatment"}:
            key = ("DISCONTINUED_AT", "status", "discontinued")
            if key not in seen:
                source_segment_ids = tuple(sources.get("status", ())) or ()
                result.append(ClinicalRelation(
                    relation_type="DISCONTINUED_AT",
                    source=source,
                    target="status",
                    value="discontinued",
                    provenance={
                        "rule": "resolved-discontinued-materialization-v2",
                        "source_segment_ids": source_segment_ids,
                    },
                    relation_id=f"{source}:DISCONTINUED_AT:status",
                    source_mention_id=source,
                    target_mention_id="status",
                    source_segment_ids=source_segment_ids,
                ))
        return tuple(result)
