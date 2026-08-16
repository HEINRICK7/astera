"""Create policy-bound, non-official V7 adjudication proposals.

This program is deliberately separate from the official human queue. It uses
only the V7 draft text, the approved semantic policy, and explicit template
patterns. It never imports or executes the resolver, never changes the draft,
and never freezes or evaluates V7. The output is a proposal for the final
human governance gate, not official gold.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from build_v7_unseen_generalization_foundation import VARIANTS


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
BATCH_DIR = RESULTS / "v7-adjudication-batches-2026-08-15"
OUT_DIR = RESULTS / "v7-ai-assisted-adjudication-2026-08-15"
POLICY = "clinical-semantic-policy-v1.2"
AI_REVIEWER = "NIEDE AI-assisted semantic governance"
AMBIGUOUS_FAMILIES = {
    "FREQUENCY_STATUS_TRANSITION",
    "DISTRIBUTED_TEMPORALITY",
    "CLINICIAN_CORRECTION",
    "PATIENT_SELF_CORRECTION",
    "ANAPHORA_SPEAKER_TRANSITION",
}

MEDICATION_CONCEPTS = {
    "losartana": "medication.losartan",
    "metformina": "medication.metformin",
    "enalapril": "medication.enalapril",
    "sertralina": "medication.sertraline",
    "atenolol": "medication.atenolol",
    "levotiroxina": "medication.levothyroxine",
    "ibuprofeno": "medication.ibuprofen",
    "dipirona": "medication.dipyrone",
    "prednisona": "medication.prednisone",
    "amlodipino": "medication.amlodipine",
}
SYMPTOM_CONCEPTS = {
    "dor": "symptom.pain",
    "tontura": "symptom.dizziness",
    "náusea": "symptom.nausea",
    "zumbido": "symptom.tinnitus",
    "fraqueza": "symptom.weakness",
    "queimação": "symptom.burning",
    "inchaço": "symptom.swelling",
    "palpitação": "symptom.palpitations",
    "coceira": "symptom.itching",
    "cólica": "symptom.cramping",
    "formigamento": "symptom.tingling",
    "tosse": "symptom.cough",
    "vertigem": "symptom.vertigo",
    "ardor": "symptom.burning",
    "rigidez": "symptom.stiffness",
    "falta de ar": "symptom.dyspnea",
    "sensibilidade": "symptom.sensitivity",
    "peso": "symptom.heaviness",
    "dormência": "symptom.numbness",
    "cansaço": "symptom.fatigue",
    "desconforto": "symptom.discomfort",
}
LATERALITY = {
    "esquerda": "left", "esquerdo": "left", "direita": "right", "direito": "right",
}


def _case_number(case_id: str) -> int:
    return int(case_id.rsplit("-", 1)[-1])


def _variant(case_id: str) -> tuple[str, ...]:
    number = _case_number(case_id)
    return VARIANTS[(number - 1) // 12]


def _segments(review: dict[str, Any]) -> dict[str, dict[str, str]]:
    return {item["segment_id"]: item for item in review["segments"]}


def _ids_with(segments: dict[str, dict[str, str]], needle: str) -> list[str]:
    return [sid for sid, segment in segments.items() if needle.casefold() in segment["text"].casefold()]


def _first_id(segments: dict[str, dict[str, str]], needle: str, fallback: int = 1) -> str:
    ids = _ids_with(segments, needle)
    if ids:
        return ids[0]
    ordered = list(segments)
    return ordered[max(0, min(fallback - 1, len(ordered) - 1))]


def _laterality(location: str) -> str | None:
    for token, value in LATERALITY.items():
        if token in location.casefold():
            return value
    return None


def _dose_parts(dose: str) -> tuple[str, str]:
    match = re.fullmatch(r"\s*([0-9]+(?:[.,][0-9]+)?)\s*(mg|mcg|g)\s*", dose, re.I)
    if not match:
        return dose, ""
    return match.group(1).replace(",", "."), match.group(2).lower()


def _provenance(**fields: list[str]) -> dict[str, list[str]]:
    return {key: value for key, value in fields.items() if value}


def _mention(
    review: dict[str, Any],
    surface: str,
    concept_id: str,
    segment_ids: list[str],
    *,
    attributes: dict[str, Any] | None = None,
    attribute_provenance: dict[str, list[str]] | None = None,
    relations: list[dict[str, Any]] | None = None,
    relation_provenance: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "surface": surface,
        "concept_id": concept_id,
        **(attributes or {}),
        "segment_ids": list(dict.fromkeys(segment_ids)),
        "attribute_provenance": attribute_provenance or {"concept": segment_ids[:1]},
        "relation_provenance": relation_provenance or {},
    }
    if relations:
        item["relations"] = relations
    return item


def _relation(relation_type: str, target: str, value: str, segment_ids: list[str]) -> dict[str, Any]:
    return {"relation_type": relation_type, "target": target, "value": value, "segment_ids": segment_ids}


def _medication(review: dict[str, Any], surface: str, *, dose: str | None = None, frequency: str | None = None,
                concept_segment: str | None = None, attribute_segment: str | None = None,
                status: str | None = None, old_dose: str | None = None) -> dict[str, Any]:
    segments = _segments(review)
    concept_segment = concept_segment or _first_id(segments, surface)
    attribute_segment = attribute_segment or concept_segment
    segment_ids = list(dict.fromkeys([concept_segment, attribute_segment]))
    attrs: dict[str, Any] = {"experiencer": "patient"}
    attr_prov = {"concept": [concept_segment], "experiencer": [attribute_segment]}
    relation_prov: dict[str, list[str]] = {}
    relations: list[dict[str, Any]] = []
    if dose is not None:
        dose_value, dose_unit = _dose_parts(dose)
        attrs.update({"dose": dose, "dose_value": dose_value, "dose_unit": dose_unit})
        for field in ("dose", "dose_value", "dose_unit"):
            attr_prov[field] = [attribute_segment]
        relations.append(_relation("HAS_DOSE", "dose", dose, [attribute_segment]))
        relation_prov["HAS_DOSE"] = [attribute_segment]
    if frequency is not None:
        attrs["frequency"] = frequency
        attr_prov["frequency"] = [attribute_segment]
        relations.append(_relation("HAS_FREQUENCY", "frequency", frequency, [attribute_segment]))
        relation_prov["HAS_FREQUENCY"] = [attribute_segment]
    if status is not None:
        attrs["status"] = status
        attr_prov["status"] = [attribute_segment]
        relation_prov["status"] = [attribute_segment]
    if old_dose is not None:
        relations.append(_relation("CHANGED_FROM", "dose", old_dose, [attribute_segment]))
        relation_prov["CHANGED_FROM"] = [attribute_segment]
    return _mention(review, surface, MEDICATION_CONCEPTS[surface], segment_ids,
                    attributes=attrs, attribute_provenance=attr_prov,
                    relations=relations, relation_provenance=relation_prov)


def _symptom(review: dict[str, Any], surface: str, *, experiencer: str = "patient",
             negated: bool | None = None, temporality: str | None = "current",
             location: str | None = None, segment_ids: list[str] | None = None,
             concept_segment: str | None = None, attribute_segment: str | None = None) -> dict[str, Any]:
    segments = _segments(review)
    concept_segment = concept_segment or _first_id(segments, surface)
    attribute_segment = attribute_segment or concept_segment
    ids = segment_ids or list(dict.fromkeys([concept_segment, attribute_segment]))
    attrs: dict[str, Any] = {"experiencer": experiencer}
    attr_prov: dict[str, list[str]] = {"concept": [concept_segment], "experiencer": [attribute_segment]}
    rel_prov: dict[str, list[str]] = {}
    relations: list[dict[str, Any]] = []
    if negated is not None:
        attrs["negated"] = negated
        attr_prov["negated"] = [attribute_segment]
    if temporality is not None:
        attrs["temporality"] = temporality
        attr_prov["temporality"] = [attribute_segment]
    if location is not None:
        side = _laterality(location)
        if side is not None:
            attrs["laterality"] = side
            attr_prov["laterality"] = [attribute_segment]
            relations.append(_relation("HAS_LATERALITY", "laterality", side, [attribute_segment]))
            rel_prov["HAS_LATERALITY"] = [attribute_segment]
    return _mention(review, surface, SYMPTOM_CONCEPTS[surface], ids,
                    attributes=attrs, attribute_provenance=attr_prov,
                    relations=relations, relation_provenance=rel_prov)


def _build_gold(review: dict[str, Any]) -> list[dict[str, Any]]:
    family = review["scenario_family"]
    med_a, med_b, symptom, location, old_dose, new_dose, frequency, temporal, _ = _variant(review["candidate_id"])
    segments = _segments(review)
    if family == "MEDICATION_RECONCILIATION":
        return [
            _medication(review, med_a, dose=old_dose, frequency=frequency, concept_segment=_first_id(segments, med_a, 1), attribute_segment=_first_id(segments, old_dose, 2), status="active"),
            _medication(review, med_b, dose=new_dose, concept_segment=_first_id(segments, med_b, 3), attribute_segment=_first_id(segments, new_dose, 4), status="active"),
        ]
    if family == "DOSE_TRANSITION":
        return [_medication(review, med_a, dose=new_dose, frequency=frequency, concept_segment=_first_id(segments, med_a, 1), attribute_segment=_first_id(segments, new_dose, 4), status="active", old_dose=old_dose)]
    if family == "MULTIPLE_SYMPTOMS":
        return [
            _symptom(review, symptom, location=location, concept_segment=_first_id(segments, symptom, 1), attribute_segment=_first_id(segments, location, 2), segment_ids=_ids_with(segments, symptom)),
            _symptom(review, "cansaço", concept_segment=_first_id(segments, "cansaço", 2), attribute_segment=_first_id(segments, "cansaço", 2), segment_ids=_ids_with(segments, "cansaço")),
        ]
    if family == "FAMILY_PATIENT_EXPERIENCER":
        return [
            _symptom(review, symptom, experiencer="family", temporality="past", concept_segment=_first_id(segments, symptom, 1), attribute_segment=_first_id(segments, symptom, 2)),
            _symptom(review, symptom, experiencer="patient", negated=True, temporality="current", concept_segment=_first_id(segments, symptom, 1), attribute_segment=_first_id(segments, symptom, 2)),
        ]
    if family == "NEGATION_REVERSAL":
        return [_symptom(review, symptom, negated=True, temporality="current", concept_segment=_first_id(segments, symptom, 1), attribute_segment=_first_id(segments, symptom, 4))]
    if family == "TOPIC_SWITCH":
        return [
            _medication(review, med_a, dose=new_dose, concept_segment=_first_id(segments, med_a, 1), attribute_segment=_first_id(segments, new_dose, 4), status="active"),
            _symptom(review, symptom, temporality="current", concept_segment=_first_id(segments, symptom, 2), attribute_segment=_first_id(segments, symptom, 4), segment_ids=_ids_with(segments, symptom)),
        ]
    if family == "ELLIPTICAL_ANSWER":
        return [_medication(review, med_a, dose=new_dose, frequency=frequency, concept_segment=_first_id(segments, med_a, 1), attribute_segment=_first_id(segments, new_dose, 2))]
    raise ValueError(f"no approved proposal template for {family}")


def _ambiguity(review: dict[str, Any]) -> tuple[str, str, list[str]]:
    family = review["scenario_family"]
    details = {
        "FREQUENCY_STATUS_TRANSITION": ("AMB-FREQ-001", "A fala declara mudança de horário, mas repete a mesma frequência como valor inicial e atual; não há valor novo inequívoco.", ["SEM-FREQ-001"]),
        "DISTRIBUTED_TEMPORALITY": ("AMB-TEMP-001", "A expressão atual 'a queixa em <local>' não identifica inequivocamente a entidade clínica; não transferir o conceito do evento antigo por anáfora implícita.", ["SEM-TEMP-001", "SEM-XSEG-001"]),
        "CLINICIAN_CORRECTION": ("AMB-CORR-001", "A autocorreção invalida a menção clínica inicial e deixa apenas uma localização; não criar uma entidade clínica artificial para a localização.", ["SEM-NEG-001", "SEM-XSEG-001"]),
        "PATIENT_SELF_CORRECTION": ("AMB-SELF-001", "A autocorreção fornece valor atual e histórico, mas a verdade do valor inicial não é suficientemente estável para gold normativo sem forçar CHANGED_FROM.", ["SEM-DOSE-001", "SEM-XSEG-001"]),
        "ANAPHORA_SPEAKER_TRANSITION": ("AMB-SPEAKER-001", "A mudança de falante informa que parte da fala era de um familiar, mas não fixa qual entidade clínica recebe o antecedente; ownership não deve ser inferido.", ["SEM-EXP-001", "SEM-XSEG-001"]),
    }
    return details[family]


def _proposal(review: dict[str, Any]) -> dict[str, Any]:
    family = review["scenario_family"]
    result = dict(review)
    result["reviewer"] = AI_REVIEWER
    result["policy_version"] = POLICY
    result["semantic_equivalence_group"] = f"template:{family}"
    result["gold_generation"] = "AI_ASSISTED_PROPOSAL_NOT_OFFICIAL"
    if family in AMBIGUOUS_FAMILIES:
        cluster, note, policies = _ambiguity(review)
        result.update({"decision": "AMBIGUOUS", "gold": None, "review_notes": note,
                       "ambiguity_cluster": cluster, "policy_ids": policies})
    else:
        result.update({"decision": "APPROVED", "gold": _build_gold(review),
                       "review_notes": "Proposta assistida por policy v1.2; requer HUMAN GATE final antes de composição/freeze.",
                       "ambiguity_cluster": None, "policy_ids": ["SEM-STATUS-001", "SEM-XSEG-001"]})
    return result


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, Any]] = []
    for batch_number in range(5, 9):
        path = next(BATCH_DIR.glob(f"v7-batch-{batch_number:02d}-*.json"))
        payload = json.loads(path.read_text(encoding="utf-8"))
        reviews = payload.get("reviews", [])
        if not reviews or any(item.get("decision") != "PENDING_HUMAN" for item in reviews):
            raise RuntimeError(f"{path.name}: expected untouched PENDING_HUMAN batch")
        proposals = [_proposal(review) for review in reviews]
        counts = {decision: sum(item["decision"] == decision for item in proposals) for decision in ("APPROVED", "REJECTED", "AMBIGUOUS", "PENDING_HUMAN")}
        output = OUT_DIR / f"v7-batch-{batch_number:02d}-ai-proposal.json"
        output.write_text(json.dumps({
            "status": "AI_ASSISTED_PROPOSAL_PENDING_HUMAN_GATE",
            "batch_id": payload["batch_id"],
            "case_range": payload["case_range"],
            "policy_version": POLICY,
            "source_batch": str(path),
            "gold_generation": "AI_ASSISTED_PROPOSAL_NOT_OFFICIAL",
            "resolver_executed": False,
            "corpus_freeze_complete": False,
            "decision_counts": counts,
            "reviews": proposals,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary.append({"batch_id": payload["batch_id"], "case_range": payload["case_range"], "output": str(output), "decision_counts": counts})
    print(json.dumps({"status": "AI_ASSISTED_PROPOSALS_READY_FOR_FINAL_HUMAN_GATE", "batches": summary, "resolver_executed": False, "official_v7_run": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
