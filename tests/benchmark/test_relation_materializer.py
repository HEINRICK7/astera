from __future__ import annotations

from labs.terminology_benchmark.clinical_projection import ClinicalRelation, ClinicalRelationMaterializer


def _relation(relation_type: str, target: str, value: str) -> ClinicalRelation:
    return ClinicalRelation(relation_type, "m1", target, value, {"source": "synthetic"})


def test_materializer_adds_current_dose_and_preserves_changed_from() -> None:
    relations = ClinicalRelationMaterializer.materialize(
        source="m1",
        owner_type="medication",
        attributes={"dose": "20 mg"},
        existing=(_relation("HAS_DOSE", "dose", "10 mg"), _relation("CHANGED_FROM", "dose", "10 mg")),
        attribute_sources={"dose": ("s2",)},
    )
    semantic = {(item.relation_type, item.target, item.value) for item in relations}
    assert semantic == {("HAS_DOSE", "dose", "20 mg"), ("CHANGED_FROM", "dose", "10 mg")}


def test_materializer_replaces_stale_relation_provenance_with_resolved_source() -> None:
    relations = ClinicalRelationMaterializer.materialize(
        source="m1",
        owner_type="medication",
        attributes={"dose": "20 mg"},
        existing=(ClinicalRelation(
            "HAS_DOSE",
            "m1",
            "dose",
            "20 mg",
            {"source": "local-projection"},
            source_segment_ids=("question",),
        ),),
        attribute_sources={"dose": ("answer",)},
    )
    assert len(relations) == 1
    assert relations[0].source_segment_ids == ("answer",)
    assert relations[0].provenance == {
        "rule": "resolved-attribute-materialization-v2",
        "attribute": "dose",
        "source_segment_ids": ("answer",),
    }


def test_materializer_does_not_attach_frequency_to_symptom() -> None:
    relations = ClinicalRelationMaterializer.materialize(
        source="m1",
        owner_type="symptom",
        attributes={"frequency": "à noite"},
        existing=(),
        attribute_sources={"frequency": ("s2",)},
    )
    assert relations == ()


def test_materializer_deduplicates_discontinued_relation() -> None:
    relations = ClinicalRelationMaterializer.materialize(
        source="m1",
        owner_type="medication",
        attributes={"status": "discontinued"},
        existing=(_relation("DISCONTINUED_AT", "status", "discontinued"), _relation("DISCONTINUED_AT", "status", "discontinued")),
        attribute_sources={"status": ("s3",)},
    )
    assert [(item.relation_type, item.target, item.value) for item in relations] == [("DISCONTINUED_AT", "status", "discontinued")]


def test_unknown_owner_does_not_create_derived_relation() -> None:
    relations = ClinicalRelationMaterializer.materialize(
        source="m1",
        owner_type=None,
        attributes={"laterality": "left", "dose": "5 mg"},
        existing=(),
    )
    assert relations == ()
