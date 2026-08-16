"""Build and freeze the human-policy-governed Diagnostic Set D1.

Gold in this file is authored from the frozen semantic policy and never by the
resolver.  The builder only creates a disjoint diagnostic corpus; it does not
execute any runtime prediction.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
OUTPUT = DATA / "d1_diagnostic_generalization_official.jsonl"
MANIFEST = RESULTS / "d1-freeze-manifest-2026-08-15.json"
DISJOINTNESS = RESULTS / "d1-disjointness-report-2026-08-15.json"
POLICY_VERSION = "1.3"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _mention(
    surface: str,
    concept_id: str,
    segment_ids: list[str],
    *,
    occurrence: int = 0,
    attribute_provenance: dict[str, list[str]] | None = None,
    relation_provenance: dict[str, list[str]] | None = None,
    relations: list[dict[str, Any]] | None = None,
    **attributes: Any,
) -> dict[str, Any]:
    defaults: dict[str, Any] = {
        "surface": surface,
        "concept_id": concept_id,
        "negated": False,
        "certainty": "confirmed",
        "temporality": "current",
        "experiencer": "patient",
        "laterality": None,
        "dose": None,
        "dose_value": None,
        "dose_unit": None,
        "frequency": None,
        "route": None,
        "status": None,
        "occurrence": occurrence,
        "relations": relations or [],
        "segment_ids": segment_ids,
        "attribute_provenance": attribute_provenance or {"mention": segment_ids},
        "relation_provenance": relation_provenance or {},
    }
    defaults.update(attributes)
    return defaults


def _case(case_id: str, family: str, segments: list[tuple[str, str, str]], gold: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "text": "\n".join(f"{speaker}: {text}" for _, speaker, text in segments),
        "language": "pt-BR",
        "source": "niede-d1-diagnostic",
        "policy_version": POLICY_VERSION,
        "scenario_family": family,
        "segments": [
            {"segment_id": segment_id, "speaker": speaker, "text": text}
            for segment_id, speaker, text in segments
        ],
        "gold": gold,
        "approval_status": "APPROVED_FOR_D1",
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
    }


CASES = [
    _case("D1-001", "ANAPHORA", [("s1", "patient", "A queimação começou no antebraço esquerdo."), ("s2", "patient", "Essa sensação piora quando digito.")], [_mention("queimação", "symptom.burning", ["s1", "s2"], laterality="left", attribute_provenance={"laterality": ["s1"], "temporality": ["s1"]})]),
    _case("D1-002", "ANAPHORA", [("s1", "patient", "Tenho um tremor discreto nas mãos."), ("s2", "clinician", "Esse sintoma acontece em repouso ou em movimento?"), ("s3", "patient", "Em repouso, principalmente à noite.")], [_mention("tremor", "symptom.tremor", ["s1", "s3"], temporality="current", attribute_provenance={"temporality": ["s1"]})]),
    _case("D1-003", "ANAPHORA", [("s1", "patient", "Senti uma pressão no peito durante a caminhada."), ("s2", "patient", "Ela desapareceu depois de alguns minutos.")], [_mention("pressão", "symptom.chest_pressure", ["s1", "s2"], temporality="past", attribute_provenance={"temporality": ["s1", "s2"]})]),

    _case("D1-004", "SPEAKER_TRANSITION", [("s1", "clinician", "A senhora mantém o remédio para tireoide?"), ("s2", "patient", "Sim, a levotiroxina continua pela manhã."), ("s3", "clinician", "E a senhora sente palpitação?"), ("s4", "patient", "Não sinto.")], [_mention("levotiroxina", "medication.levothyroxine", ["s1", "s2"], frequency="pela manhã", status="active", attribute_provenance={"frequency": ["s2"], "status": ["s2"]}), _mention("palpitação", "symptom.palpitations", ["s3", "s4"], negated=True, attribute_provenance={"negated": ["s4"]})]),
    _case("D1-005", "SPEAKER_TRANSITION", [("s1", "clinician", "Quem usa o spray nasal?"), ("s2", "patient", "Eu uso a budesonida todas as noites."), ("s3", "clinician", "E sua esposa?"), ("s4", "patient", "Ela não usa.")], [_mention("budesonida", "medication.budesonide", ["s1", "s2"], frequency="todas as noites", status="active", attribute_provenance={"frequency": ["s2"], "status": ["s2"]})]),
    _case("D1-006", "SPEAKER_TRANSITION", [("s1", "patient", "Meu irmão trouxe o laudo da consulta."), ("s2", "clinician", "O diagnóstico dele é confirmado?"), ("s3", "patient", "O diabetes dele foi confirmado no inverno." )], [_mention("diabetes", "condition.diabetes", ["s1", "s3"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["s1", "s3"], "temporality": ["s3"]})]),

    _case("D1-007", "DISTRIBUTED_TEMPORALITY", [("s1", "patient", "A enxaqueca está controlada hoje."), ("s2", "patient", "A crise que tive no outono ficou para trás." )], [_mention("enxaqueca", "condition.migraine", ["s1", "s2"], temporality="current", attribute_provenance={"temporality": ["s1"]})]),
    _case("D1-008", "DISTRIBUTED_TEMPORALITY", [("s1", "patient", "Tive uma queda no corredor."), ("s2", "patient", "O episódio aconteceu há três meses, sem repetição." )], [_mention("queda", "event.fall", ["s1", "s2"], temporality="past", attribute_provenance={"temporality": ["s2"]})]),
    _case("D1-009", "DISTRIBUTED_TEMPORALITY", [("s1", "patient", "A tosse começou na segunda-feira."), ("s2", "clinician", "Ainda existe tosse agora?"), ("s3", "patient", "Existe, mas está bem mais fraca." )], [_mention("tosse", "symptom.cough", ["s1", "s2", "s3"], temporality="current", attribute_provenance={"temporality": ["s3"]})]),

    _case("D1-010", "MEDICATION_RECONCILIATION", [("s1", "patient", "Eu tomava carvedilol de 25 mg."), ("s2", "patient", "Na verdade, o comprimido é de 12,5 mg desde a alta." )], [_mention("carvedilol", "medication.carvedilol", ["s1", "s2"], dose="12,5 mg", dose_value="12.5", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "25 mg"}], attribute_provenance={"dose": ["s2"], "dose_value": ["s2"], "dose_unit": ["s2"], "status": ["s2"]}, relation_provenance={"CHANGED_FROM": ["s2"]})]),
    _case("D1-011", "MEDICATION_RECONCILIATION", [("s1", "patient", "A lista antiga tinha rosuvastatina."), ("s2", "clinician", "Você ainda toma esse medicamento?"), ("s3", "patient", "Não, foi retirado da receita no mês passado." )], [_mention("rosuvastatina", "medication.rosuvastatin", ["s1", "s3"], status="discontinued", temporality="current", attribute_provenance={"status": ["s3"], "temporality": ["s3"]}, relations=[{"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"}], relation_provenance={"DISCONTINUED_AT": ["s3"]})]),
    _case("D1-012", "MEDICATION_RECONCILIATION", [("s1", "patient", "Uso valsartana na rotina."), ("s2", "clinician", "A valsartana permanece na lista atual?"), ("s3", "patient", "Sim, foi mantida sem interrupção." )], [_mention("valsartana", "medication.valsartan", ["s1", "s3"], status="active", attribute_provenance={"status": ["s3"]})]),

    _case("D1-013", "DOSE_TRANSITION", [("s1", "patient", "A gabapentina estava em 300 mg."), ("s2", "clinician", "Qual é a dose depois do ajuste?"), ("s3", "patient", "Ficou em 400 mg por cápsula." )], [_mention("gabapentina", "medication.gabapentin", ["s1", "s3"], dose="400 mg", dose_value="400", dose_unit="mg", status="active", attribute_provenance={"dose": ["s3"], "dose_value": ["s3"], "dose_unit": ["s3"], "status": ["s3"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "300 mg"}], relation_provenance={"CHANGED_FROM": ["s3"]})]),
    _case("D1-014", "DOSE_TRANSITION", [("s1", "patient", "O adesivo de nicotina era de 14 mg."), ("s2", "patient", "Depois da consulta, passei para 7 mg." )], [_mention("adesivo de nicotina", "medication.nicotine_patch", ["s1", "s2"], dose="7 mg", dose_value="7", dose_unit="mg", status="active", attribute_provenance={"dose": ["s2"], "dose_value": ["s2"], "dose_unit": ["s2"], "status": ["s2"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "14 mg"}], relation_provenance={"CHANGED_FROM": ["s2"]})]),
    _case("D1-015", "DOSE_TRANSITION", [("s1", "clinician", "A dose da sertralina mudou?"), ("s2", "patient", "Sim. Antes eram 50 mg e agora são 75 mg." )], [_mention("sertralina", "medication.sertraline", ["s1", "s2"], dose="75 mg", dose_value="75", dose_unit="mg", status="active", attribute_provenance={"dose": ["s2"], "dose_value": ["s2"], "dose_unit": ["s2"], "status": ["s2"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "50 mg"}], relation_provenance={"CHANGED_FROM": ["s2"]})]),

    _case("D1-016", "FREQUENCY_TRANSITION", [("s1", "patient", "Eu usava o inalador duas vezes ao dia."), ("s2", "patient", "Com a melhora, reduzi para uma vez ao dia." )], [_mention("inalador", "medication.inhaler", ["s1", "s2"], frequency="uma vez ao dia", status="active", attribute_provenance={"frequency": ["s2"], "status": ["s2"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "duas vezes ao dia"}], relation_provenance={"CHANGED_FROM": ["s2"]})]),
    _case("D1-017", "FREQUENCY_TRANSITION", [("s1", "patient", "A hidroclorotiazida era tomada pela manhã."), ("s2", "clinician", "Mudou o horário?"), ("s3", "patient", "Agora tomo à noite, depois do jantar." )], [_mention("hidroclorotiazida", "medication.hydrochlorothiazide", ["s1", "s3"], frequency="à noite", status="active", attribute_provenance={"frequency": ["s3"], "status": ["s3"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "pela manhã"}], relation_provenance={"CHANGED_FROM": ["s3"]})]),
    _case("D1-018", "FREQUENCY_TRANSITION", [("s1", "patient", "Tomo o suplemento em dias alternados."), ("s2", "patient", "Na orientação nova, ficou todos os dias." )], [_mention("suplemento", "medication.supplement", ["s1", "s2"], frequency="todos os dias", status="active", attribute_provenance={"frequency": ["s2"], "status": ["s2"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "dias alternados"}], relation_provenance={"CHANGED_FROM": ["s2"]})]),

    _case("D1-019", "FAMILY_PATIENT_EXPERIENCER", [("s1", "patient", "Minha tia teve artrite na velhice."), ("s2", "clinician", "E você sente dor nas mãos?"), ("s3", "patient", "Eu sinto só rigidez pela manhã." )], [_mention("artrite", "condition.arthritis", ["s1"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["s1"], "temporality": ["s1"]}), _mention("rigidez", "symptom.stiffness", ["s3"], experiencer="patient", temporality="current", attribute_provenance={"experiencer": ["s3"], "temporality": ["s3"]})]),
    _case("D1-020", "FAMILY_PATIENT_EXPERIENCER", [("s1", "clinician", "Há casos de epilepsia na família?"), ("s2", "patient", "Meu pai teve, mas eu nunca tive crise." )], [_mention("epilepsia", "condition.epilepsy", ["s1", "s2"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["s2"], "temporality": ["s2"]}), _mention("crise", "symptom.seizure", ["s2"], negated=True, experiencer="patient", attribute_provenance={"negated": ["s2"], "experiencer": ["s2"]})]),
    _case("D1-021", "FAMILY_PATIENT_EXPERIENCER", [("s1", "patient", "Meu filho apresentou alergia quando era pequeno."), ("s2", "patient", "Hoje eu não tenho alergia conhecida." )], [_mention("alergia", "condition.allergy", ["s1"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["s1"], "temporality": ["s1"]}), _mention("alergia", "condition.allergy", ["s2"], occurrence=1, negated=True, experiencer="patient", temporality="current", attribute_provenance={"negated": ["s2"], "experiencer": ["s2"], "temporality": ["s2"]})]),

    _case("D1-022", "NEGATION_REVERSAL", [("s1", "patient", "Eu não tinha falta de ar."), ("s2", "patient", "Corrigindo: agora tenho falta de ar ao subir escadas." )], [_mention("falta de ar", "symptom.dyspnea", ["s1", "s2"], negated=False, temporality="current", attribute_provenance={"negated": ["s2"], "temporality": ["s2"]})]),
    _case("D1-023", "NEGATION_REVERSAL", [("s1", "clinician", "Você sente náusea?"), ("s2", "patient", "Não. Quer dizer, senti náusea esta manhã, mas já passou." )], [_mention("náusea", "symptom.nausea", ["s1", "s2"], negated=False, temporality="past", attribute_provenance={"negated": ["s2"], "temporality": ["s2"]})]),
    _case("D1-024", "NEGATION_REVERSAL", [("s1", "patient", "Não tive tontura durante a viagem."), ("s2", "patient", "Na verdade, tive tontura ao chegar." )], [_mention("tontura", "symptom.dizziness", ["s1", "s2"], negated=False, temporality="past", attribute_provenance={"negated": ["s2"], "temporality": ["s2"]})]),

    _case("D1-025", "TOPIC_SWITCH", [("s1", "patient", "A dor lombar melhorou."), ("s2", "patient", "Falando de outra coisa, meu estômago queima depois do café." )], [_mention("dor lombar", "symptom.back_pain", ["s1"], temporality="past", attribute_provenance={"temporality": ["s1"]}), _mention("estômago", "anatomical.stomach", ["s2"], attribute_provenance={"mention": ["s2"]})]),
    _case("D1-026", "TOPIC_SWITCH", [("s1", "patient", "A amlodipina continua em 5 mg."), ("s2", "patient", "Mudando de assunto, a coceira aparece no pescoço." )], [_mention("amlodipina", "medication.amlodipine", ["s1"], dose="5 mg", dose_value="5", dose_unit="mg", status="active", attribute_provenance={"dose": ["s1"], "dose_value": ["s1"], "dose_unit": ["s1"], "status": ["s1"]}), _mention("coceira", "symptom.itching", ["s2"], laterality=None, attribute_provenance={"mention": ["s2"]})]),
    _case("D1-027", "TOPIC_SWITCH", [("s1", "clinician", "Vamos fechar o assunto da glicose."), ("s2", "patient", "Sobre a visão, vejo pontos brilhantes à noite." )], [_mention("glicose", "condition.hyperglycemia", ["s1"], attribute_provenance={"mention": ["s1"]}), _mention("pontos brilhantes", "symptom.visual_photopsia", ["s2"], temporality="current", attribute_provenance={"temporality": ["s2"]})]),

    _case("D1-028", "ELLIPTICAL_ANSWER", [("s1", "clinician", "Qual é a dose do omeprazol?"), ("s2", "patient", "Quarenta." )], [_mention("omeprazol", "medication.omeprazole", ["s1", "s2"], dose="40 mg", dose_value="40", dose_unit="mg", status="active", attribute_provenance={"dose": ["s2"], "dose_value": ["s2"], "dose_unit": ["s2"], "status": ["s1"]})]),
    _case("D1-029", "ELLIPTICAL_ANSWER", [("s1", "clinician", "Em que lado é a dor no ombro?"), ("s2", "patient", "Direito." )], [_mention("dor", "symptom.shoulder_pain", ["s1", "s2"], laterality="right", attribute_provenance={"laterality": ["s2"]})]),
    _case("D1-030", "ELLIPTICAL_ANSWER", [("s1", "clinician", "Você ainda usa o adesivo?"), ("s2", "patient", "Parei." )], [_mention("adesivo", "medication.patch", ["s1", "s2"], status="discontinued", temporality="current", attribute_provenance={"status": ["s2"], "temporality": ["s2"]}, relations=[{"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"}], relation_provenance={"DISCONTINUED_AT": ["s2"]})]),

    _case("D1-031", "CLINICIAN_CORRECTION", [("s1", "clinician", "O prontuário indica hipertensão."), ("s2", "clinician", "Correção: era apenas uma suspeita, não um diagnóstico confirmado." )], [_mention("hipertensão", "condition.hypertension", ["s1", "s2"], certainty="possible", attribute_provenance={"certainty": ["s2"]})]),
    _case("D1-032", "CLINICIAN_CORRECTION", [("s1", "clinician", "A cirurgia foi em março."), ("s2", "clinician", "Retifico: o procedimento foi em abril." )], [_mention("cirurgia", "procedure.surgery", ["s1", "s2"], temporality="past", attribute_provenance={"temporality": ["s2"]})]),
    _case("D1-033", "CLINICIAN_CORRECTION", [("s1", "clinician", "A lesão é no joelho direito."), ("s2", "clinician", "Desculpe, a anotação correta é joelho esquerdo." )], [_mention("lesão", "condition.lesion", ["s1", "s2"], laterality="left", attribute_provenance={"laterality": ["s2"]})]),

    _case("D1-034", "PATIENT_SELF_CORRECTION", [("s1", "patient", "Minha mãe teve asma."), ("s2", "patient", "Quer dizer, foi minha irmã, não minha mãe." )], [_mention("asma", "condition.asthma", ["s1", "s2"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["s2"], "temporality": ["s1"]})]),
    _case("D1-035", "PATIENT_SELF_CORRECTION", [("s1", "patient", "Tomo atenolol à noite."), ("s2", "patient", "Não, corrijo: tomo de manhã." )], [_mention("atenolol", "medication.atenolol", ["s1", "s2"], frequency="de manhã", status="active", attribute_provenance={"frequency": ["s2"], "status": ["s1"]}, relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "à noite"}], relation_provenance={"CHANGED_FROM": ["s2"]})]),
    _case("D1-036", "PATIENT_SELF_CORRECTION", [("s1", "patient", "O exame mostrou anemia."), ("s2", "patient", "Melhor dizendo, mostrou apenas ferro baixo." )], [_mention("anemia", "condition.anemia", ["s1", "s2"], certainty="possible", attribute_provenance={"certainty": ["s2"]})]),
]


def _validate_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [record["case_id"] for record in records]
    if len(records) != 36:
        errors.append(f"expected 36 cases, found {len(records)}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate case ids")
    for record in records:
        segment_ids = {segment["segment_id"] for segment in record["segments"]}
        if not record["gold"]:
            errors.append(f"{record['case_id']}: no gold")
        for mention in record["gold"]:
            if not any(mention["surface"].casefold() in segment["text"].casefold() for segment in record["segments"]):
                errors.append(f"{record['case_id']}: surface absent: {mention['surface']}")
            if not set(mention["segment_ids"]).issubset(segment_ids):
                errors.append(f"{record['case_id']}: invalid segment ownership")
            for source_map in (mention.get("attribute_provenance", {}), mention.get("relation_provenance", {})):
                for sources in source_map.values():
                    if not set(sources).issubset(segment_ids):
                        errors.append(f"{record['case_id']}: invalid provenance")
    return errors


def _disjointness(records: list[dict[str, Any]]) -> dict[str, Any]:
    corpus_paths = sorted(DATA.glob("*.jsonl")) + sorted(DATA.glob("*.json"))
    known_texts: dict[str, str] = {}
    for path in corpus_paths:
        if path == OUTPUT:
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip() or not line.lstrip().startswith("{"):
                    continue
                item = json.loads(line)
                if isinstance(item, dict) and item.get("text"):
                    known_texts[_normalize(item["text"])] = str(path)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    collisions = [
        {"case_id": record["case_id"], "source": known_texts[_normalize(record["text"])]}
        for record in records
        if _normalize(record["text"]) in known_texts
    ]
    return {
        "status": "PASS" if not collisions else "FAIL",
        "candidate_cases": len(records),
        "compared_corpus_files": [str(path) for path in corpus_paths if path != OUTPUT],
        "exact_normalized_text_collisions": collisions,
        "collision_count": len(collisions),
        "trace_test_fixture_texts_used": False,
        "holdouts_consumed_reused": False,
        "v7_reused": False,
    }


def main() -> None:
    errors = _validate_records(CASES)
    disjointness = _disjointness(CASES)
    DISJOINTNESS.write_text(json.dumps(disjointness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors or disjointness["status"] != "PASS":
        raise RuntimeError({"validation_errors": errors, "disjointness": disjointness})
    OUTPUT.write_text("\n".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in CASES) + "\n", encoding="utf-8")
    manifest = {
        "status": "D1_FROZEN",
        "corpus_version": "D1",
        "policy_version": POLICY_VERSION,
        "case_count": len(CASES),
        "mention_count": sum(len(record["gold"]) for record in CASES),
        "relation_count": sum(len(mention.get("relations", [])) for record in CASES for mention in record["gold"]),
        "scenario_families": sorted({record["scenario_family"] for record in CASES}),
        "official_corpus": str(OUTPUT),
        "official_corpus_checksum": _sha256(OUTPUT),
        "policy_checksum": _sha256(POLICY),
        "disjointness_report": str(DISJOINTNESS),
        "disjointness_checksum": _sha256(DISJOINTNESS),
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "gold_immutable_after_freeze": True,
        "one_shot_run_count": 0,
        "blind_run_authorized": True,
        "resolver_repair": "NOT_AUTHORIZED",
        "v7": "CONSUMED_IMMUTABLE",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
        "freeze_validation": {"structural": "PASS", "gold_provenance": "PASS", "policy_conformance": "PASS", "disjointness": "PASS"},
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
