"""Build the human-authored independent/conversational V6 draft."""
from __future__ import annotations

import json
from pathlib import Path

from .corpus import CONTEXT_VALIDATION_V6_DRAFT_PATH


def _mention(surface: str, concept_id: str, **fields: object) -> dict[str, object]:
    return {"surface": surface, "concept_id": concept_id, **fields}


def _case(case_id: str, text: str, gold: list[dict[str, object]], source: str, segments: list[dict[str, str]] | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "case_id": case_id,
        "language": "pt-BR",
        "text": text,
        "source": source,
        "gold": gold,
    }
    if segments:
        payload["segments"] = segments
    return payload


def _independent_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    pairs = (
        ("dor no joelho esquerdo", "formigamento na mão direita"),
        ("queimação no pé esquerdo", "peso na perna direita"),
        ("dor no ombro esquerdo", "fraqueza no braço direito"),
        ("inchaço no tornozelo esquerdo", "dormência na coxa direita"),
        ("pontada no lado esquerdo", "sensibilidade no lado direito"),
        ("dor na mama esquerda", "nódulo na axila direita"),
        ("coceira na mão esquerda", "ardor no pé direito"),
        ("rigidez no quadril esquerdo", "dor na panturrilha direita"),
        ("tremor na mão esquerda", "perda de força na perna direita"),
        ("desconforto no ouvido esquerdo", "zumbido no ouvido direito"),
    )
    for index, (first, second) in enumerate(pairs, 1):
        text = f"Refere {first} ao acordar e {second} depois de caminhar."
        cases.append(_case(
            f"v6-i-{index:03d}", text,
            [_mention(first, f"symptom.independent_{index}_a", laterality="left"),
             _mention(second, f"symptom.independent_{index}_b", laterality="right")],
            "independent",
        ))

    negated = (
        ("febre", "tosse seca"), ("náusea", "dor abdominal"),
        ("calafrio", "cansaço"), ("vômito", "azia"),
        ("dispneia", "chiado"), ("sangramento", "tontura"),
        ("dor torácica", "palpitação"), ("diarreia", "cólica"),
        ("prurido", "vermelhidão"), ("desmaio", "fraqueza"),
    )
    for offset, (first, second) in enumerate(negated, 11):
        text = f"Nega {first}, mas relata {second} desde ontem."
        cases.append(_case(
            f"v6-i-{offset:03d}", text,
            [_mention(first, f"symptom.independent_{offset}_a", negated=True),
             _mention(second, f"symptom.independent_{offset}_b", temporality="current")],
            "independent",
        ))

    family = (
        ("diabetes", "dor no peito"), ("hipertensão", "falta de ar"),
        ("câncer de mama", "nódulo"), ("asma", "chiado"),
        ("AVC", "tontura"), ("tuberculose", "tosse"),
        ("lúpus", "dor articular"), ("infarto", "palpitação"),
        ("epilepsia", "desmaio"), ("alergia", "urticária"),
    )
    for offset, (condition, symptom) in enumerate(family, 21):
        text = f"A mãe teve {condition}, mas o paciente não relata {symptom}."
        cases.append(_case(
            f"v6-i-{offset:03d}", text,
            [_mention(condition, f"condition.independent_{offset}_a", temporality="past", experiencer="family"),
             _mention(symptom, f"symptom.independent_{offset}_b", negated=True)],
            "independent",
        ))

    medication = (
        ("losartana", "medication.losartan", "50 mg", "metformina", "medication.metformin", "850 mg"),
        ("enalapril", "medication.enalapril", "10 mg", "dipirona", "medication.dipyrone", "1 g"),
        ("sertralina", "medication.sertraline", "50 mg", "omeprazol", "medication.omeprazole", "20 mg"),
        ("atenolol", "medication.atenolol", "25 mg", "ibuprofeno", "medication.ibuprofen", "400 mg"),
        ("amoxicilina", "medication.amoxicillin", "500 mg", "paracetamol", "medication.paracetamol", "750 mg"),
        ("pregabalina", "medication.pregabalin", "75 mg", "cálcio", "medication.calcium", "500 mg"),
        ("hidroclorotiazida", "medication.hydrochlorothiazide", "25 mg", "sinvastatina", "medication.simvastatin", "20 mg"),
        ("clonidina", "medication.clonidine", "0,1 mg", "insulina", "medication.insulin", "10 UI"),
        ("gabapentina", "medication.gabapentin", "300 mg", "vitamina D", "medication.vitamin_d", "1000 UI"),
        ("carvedilol", "medication.carvedilol", "6,25 mg", "budesonida", "medication.budesonide", "2 jatos"),
    )
    for offset, (first, first_id, first_dose, second, second_id, second_dose) in enumerate(medication, 31):
        text = f"Usa {first} {first_dose} pela manhã e {second} {second_dose} à noite."
        cases.append(_case(
            f"v6-i-{offset:03d}", text,
            [_mention(first, first_id, dose=first_dose, dose_value=first_dose.split()[0].replace(",", "."), dose_unit=first_dose.split()[1], frequency="pela manhã", status="active"),
             _mention(second, second_id, dose=second_dose, dose_value=second_dose.split()[0].replace(",", "."), dose_unit=second_dose.split()[1], frequency="à noite", status="active")],
            "independent",
        ))

    uncertainty = (
        ("pneumonia", "falta de ar"), ("virose", "febre"),
        ("crise convulsiva", "mordedura na língua"), ("alergia", "urticária"),
        ("fratura", "inchaço"), ("migraine", "fotofobia"),
        ("apendicite", "dor abdominal"), ("anemia", "palidez"),
        ("infecção urinária", "ardor ao urinar"), ("refluxo", "azia"),
    )
    for offset, (condition, symptom) in enumerate(uncertainty, 41):
        text = f"Possível {condition}, sem confirmação; nega {symptom}."
        cases.append(_case(
            f"v6-i-{offset:03d}", text,
            [_mention(condition, f"condition.independent_{offset}_a", certainty="possible"),
             _mention(symptom, f"symptom.independent_{offset}_b", negated=True)],
            "independent",
        ))

    temporal = (
        ("cirurgia no ombro", "dormência no braço"), ("queda", "dor no quadril"),
        ("pneumonia", "tosse"), ("lesão no joelho", "inchaço no tornozelo"),
        ("fratura na mão", "rigidez nos dedos"), ("infarto", "cansaço"),
        ("crise de asma", "chiado"), ("dor lombar", "formigamento na perna"),
        ("trombose", "peso na panturrilha"), ("otite", "zumbido"),
    )
    for offset, (past_event, current_symptom) in enumerate(temporal, 51):
        text = f"Teve {past_event} há anos, mas hoje sente {current_symptom}."
        cases.append(_case(
            f"v6-i-{offset:03d}", text,
            [_mention(past_event, f"event.independent_{offset}_a", temporality="past"),
             _mention(current_symptom, f"symptom.independent_{offset}_b", temporality="current")],
            "independent",
        ))
    return cases


def _realistic_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    variants = (
        ("Tá sem febre mas tá tossindo e meio cansado", "febre", "tossindo", "cansado"),
        ("Não tem dor, só uma pressão no peito e falta de ar", "dor", "pressão no peito", "falta de ar"),
        ("Diz que não vomitou mas teve enjoo e uma azia forte", "vomitou", "enjoo", "azia"),
        ("Sem tontura, só fraqueza e visão meio turva", "tontura", "fraqueza", "visão meio turva"),
        ("Não sente coceira mas apareceu vermelhidão e inchaço", "coceira", "vermelhidão", "inchaço"),
        ("Nega palpitação, refere cansaço e peso no peito", "palpitação", "cansaço", "peso no peito"),
        ("Tá sem náusea, porém com cólica e barriga estufada", "náusea", "cólica", "barriga estufada"),
        ("Não relata calafrio mas teve febre e dor no corpo", "calafrio", "febre", "dor no corpo"),
        ("Diz que não tem falta de ar, só chiado e tosse de manhã", "falta de ar", "chiado", "tosse"),
        ("Sem sangramento, mas com dor e uma secreção estranha", "sangramento", "dor", "secreção"),
    )
    for offset, (text, first, second, third) in enumerate(variants, 1):
        for replica in range(3):
            suffix = (" hoje", " desde ontem", " depois do almoço")[replica]
            full_text = text + suffix + "."
            cases.append(_case(
                f"v6-r-{offset:03d}-{replica + 1}", full_text,
                [_mention(first, f"symptom.realistic_{offset}_a", negated=True),
                 _mention(second, f"symptom.realistic_{offset}_b"),
                 _mention(third, f"symptom.realistic_{offset}_c")],
                "realistic",
            ))
    return cases


def _conversation_cases() -> list[dict[str, object]]:
    conversations = (
        ("Ainda está tomando losartana?", "Não, parei semana passada e não tive tontura.", "losartana", "medication.losartan", {"status": "discontinued", "temporality": "past"}, (("tontura", "symptom.dizziness", {"negated": True}), ("semana passada", "time.last_week", {"temporality": "past"})), "answer",),
        ("Sua mãe teve câncer e diabetes?", "Teve, de mama.", "câncer", "condition.cancer", {"experiencer": "family", "temporality": "past"}, (("diabetes", "condition.diabetes", {"experiencer": "family", "temporality": "past"}), ("mãe", "person.mother", {"experiencer": "family"})), "question",),
        ("A dor continua?", "Não, agora só sinto formigamento na mão direita e cansaço.", "dor", "symptom.pain", {"negated": True, "temporality": "current"}, (("formigamento na mão direita", "symptom.paresthesia", {"laterality": "right"}), ("cansaço", "symptom.fatigue", {"temporality": "current"})), "answer",),
        ("Ele ainda usa a bombinha?", "Usa quando começa com chiado, mas não sente falta de ar.", "bombinha", "device.inhaler", {"status": "active", "experiencer": "patient"}, (("chiado", "symptom.wheezing", {"experiencer": "patient"}), ("falta de ar", "symptom.dyspnea", {"negated": True})), "answer",),
        ("A mãe tinha diabetes e hipertensão?", "Sim, mas eu não tenho tosse.", "diabetes", "condition.diabetes", {"experiencer": "family", "temporality": "past"}, (("hipertensão", "condition.hypertension", {"experiencer": "family", "temporality": "past"}), ("tosse", "symptom.cough", {"negated": True})), "question",),
    )
    cases: list[dict[str, object]] = []
    qualifiers = ("na consulta de hoje", "no retorno desta semana", "durante a revisão clínica")
    for offset, (question, answer, surface, concept, fields, extras, primary_field_source) in enumerate(conversations, 1):
        for replica in range(3):
            sid1 = f"seg_{offset:02d}_{replica}_01"
            sid2 = f"seg_{offset:02d}_{replica}_02"
            answer_variant = f"{answer} {qualifiers[replica]}"
            segments = [
                {"segment_id": sid1, "speaker": "clinician", "text": question},
                {"segment_id": sid2, "speaker": "patient", "text": answer_variant},
            ]
            text = f"Médico: {question}\nPaciente: {answer_variant}"
            primary_source = sid2 if primary_field_source == "answer" else sid1
            gold = [_mention(
                surface,
                concept,
                segment_ids=(sid1,),
                attribute_provenance={"concept": (sid1,), **{field: (primary_source,) for field in fields}},
                relation_provenance={field: (primary_source,) for field in fields},
                **fields,
            )]
            gold.extend(
                _mention(
                    extra_surface,
                    extra_concept,
                    segment_ids=(sid2,),
                    attribute_provenance={"concept": (sid2,), **{field: (sid2,) for field in extra_fields}},
                    relation_provenance={field: (sid2,) for field in extra_fields},
                    **extra_fields,
                )
                for extra_surface, extra_concept, extra_fields in extras
            )
            cases.append(_case(
                f"v6-c-{offset:03d}-{replica + 1}", text,
                gold,
                "realistic",
                segments,
            ))
    return cases


def build() -> list[dict[str, object]]:
    cases = _independent_cases() + _realistic_cases() + _conversation_cases()
    assert len(cases) == 105
    assert sum(len(case["gold"]) for case in cases) == 255
    return cases


def main() -> None:
    cases = build()
    CONTEXT_VALIDATION_V6_DRAFT_PATH.write_text(
        "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases),
        encoding="utf-8",
    )
    print(json.dumps({"status": "draft-only", "cases": len(cases), "mentions": 255, "output": str(CONTEXT_VALIDATION_V6_DRAFT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
