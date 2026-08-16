from __future__ import annotations

from pathlib import Path

import pytest

from labs.terminology_benchmark.clinical_conversational_semantics import ResolvedClinicalSemantics
from labs.terminology_benchmark.clinical_projection import ClinicalRelation, ClinicalRelationCompiler, ClinicalRelationSet


def _resolved(*, attributes: dict[str, object], owner_type: str, owner_id: str = "m1", provenance: dict[str, object] | None = None) -> ResolvedClinicalSemantics:
    ownership = {
        field: {
            "owner_type": owner_type,
            "owner_mention_id": owner_id,
            "source_segment_ids": ("answer",),
        }
        for field, value in attributes.items()
        if value is not None
    }
    return ResolvedClinicalSemantics(
        resolved_mentions=(),
        resolved_attributes=attributes,
        resolved_relations=(),
        unresolved=(),
        provenance={
            "owner_type": owner_type,
            "owner_mention_id": owner_id,
            "attribute_ownership": ownership,
            **(provenance or {}),
        },
    )


def _semantic(relations: ClinicalRelationSet) -> set[tuple[str, str, str, str]]:
    return {(item.relation_type, item.source, item.target, item.value) for item in relations}


def test_compiler_emits_current_dose_and_transition_only() -> None:
    resolved = _resolved(
        attributes={"dose": "100 mg", "dose_value": "100", "dose_unit": "mg"},
        owner_type="medication",
        provenance={"transition_evidence": [{
            "relation_type": "CHANGED_FROM",
            "source": "candidate",
            "target": "dose",
            "value": "50 mg",
            "source_segment_ids": ["history"],
            "provenance": {"source_segment_ids": ["history"]},
        }]},
    )
    result = ClinicalRelationCompiler().compile(resolved)
    assert _semantic(result) == {
        ("HAS_DOSE", "m1", "dose", "100 mg"),
        ("CHANGED_FROM", "m1", "dose", "50 mg"),
    }
    assert not any(item.value == "50 mg" and item.relation_type == "HAS_DOSE" for item in result)


def test_current_attribute_is_the_only_has_relation_source() -> None:
    resolved = _resolved(
        attributes={"dose": "100 mg", "dose_value": "100", "dose_unit": "mg"},
        owner_type="medication",
        provenance={
            "historical_attributes": {"dose": "50 mg"},
            "transition_evidence": [{
                "relation_type": "CHANGED_FROM",
                "source": "m1",
                "target": "dose",
                "value": "50 mg",
                "source_segment_ids": ["history"],
                "provenance": {"source_segment_ids": ["history"]},
            }],
        },
    )
    relations = ClinicalRelationCompiler().compile(resolved).relations
    assert ("HAS_DOSE", "m1", "dose", "100 mg") in _semantic(ClinicalRelationSet(relations))
    assert ("CHANGED_FROM", "m1", "dose", "50 mg") in _semantic(ClinicalRelationSet(relations))
    assert not any(
        item.relation_type == "HAS_DOSE" and item.value == "50 mg"
        for item in relations
    )


def test_compiler_blocks_incompatible_owner() -> None:
    result = ClinicalRelationCompiler().compile(_resolved(
        attributes={"dose": "25 mg", "laterality": "left"},
        owner_type="symptom",
    ))
    assert _semantic(result) == {("HAS_LATERALITY", "m1", "laterality", "left")}


def test_compiler_deduplicates_transition_signals() -> None:
    resolved = _resolved(
        attributes={"frequency": "à noite"},
        owner_type="medication",
        provenance={"transition_evidence": [
            {"relation_type": "CHANGED_FROM", "source": "m1", "target": "frequency", "value": "pela manhã"},
            {"relation_type": "CHANGED_FROM", "source": "m1", "target": "frequency", "value": "pela manhã"},
        ]},
    )
    result = ClinicalRelationCompiler().compile(resolved)
    assert len(result.relations) == 2


def test_compiler_suppresses_lifecycle_relation_for_non_medication_owner() -> None:
    result = ClinicalRelationCompiler().compile(_resolved(
        attributes={"status": "discontinued"},
        owner_type="symptom",
    ))
    assert result.relations == ()


def test_compiler_binds_attribute_provenance() -> None:
    resolved = _resolved(
        attributes={"laterality": "right"},
        owner_type="symptom",
        provenance={"attribute_ownership": {
            "laterality": {
                "owner_type": "symptom",
                "owner_mention_id": "m1",
                "source_segment_ids": ("answer-2",),
            },
        }},
    )
    relation = ClinicalRelationCompiler().compile(resolved).relations[0]
    assert relation.source_segment_ids == ("answer-2",)
    assert relation.provenance["rule"] == "clinical-relation-compiler-v1"


def test_relation_set_rejects_duplicate_final_relations() -> None:
    relation = ClinicalRelation("HAS_DOSE", "m1", "dose", "10 mg", {})
    with pytest.raises(ValueError):
        ClinicalRelationSet((relation, relation))


def test_relation_set_rejects_post_compile_mutation() -> None:
    relation = ClinicalRelation("HAS_DOSE", "m1", "dose", "10 mg", {})
    result = ClinicalRelationSet((relation,))
    with pytest.raises(TypeError):
        result.relations[0].provenance["rule"] = "mutated"


def test_architecture_has_one_final_projection_relation_assignment() -> None:
    root = Path(__file__).resolve().parents[2]
    sources = (
        root / "labs/terminology_benchmark/clinical_projection.py",
        root / "labs/terminology_benchmark/cross_segment_context.py",
        root / "labs/terminology_benchmark/context_safety.py",
        root / "labs/terminology_benchmark/clinical_conversational_semantics.py",
    )
    assignments = sum(path.read_text(encoding="utf-8").count('projection["relations"] =') for path in sources)
    assert assignments == 1
    assert 'projection["relations"] =' not in (root / "labs/terminology_benchmark/cross_segment_context.py").read_text(encoding="utf-8")
    assert 'projection["relations"] =' not in (root / "labs/terminology_benchmark/context_safety.py").read_text(encoding="utf-8")
