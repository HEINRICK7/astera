"""Build and freeze the unseen Diagnostic Generalization Set D2.

Gold is authored from the human-governed clinical semantic policy.  This
module never imports or executes the resolver; it only creates and validates
the independent corpus and its manifest.
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
OUTPUT = DATA / "d2_diagnostic_generalization_official.jsonl"
MANIFEST = RESULTS / "D2_FREEZE_MANIFEST.json"
DISJOINTNESS = RESULTS / "d2-disjointness-report-2026-08-15.json"
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
    values: dict[str, Any] = {
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
    values.update(attributes)
    return values


def _case(case_id: str, family: str, segments: list[tuple[str, str, str]], gold: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "text": "\n".join(f"{speaker}: {text}" for _, speaker, text in segments),
        "language": "pt-BR",
        "source": "niede-d2-diagnostic",
        "policy_version": POLICY_VERSION,
        "scenario_family": family,
        "segments": [
            {"segment_id": segment_id, "speaker": speaker, "text": text}
            for segment_id, speaker, text in segments
        ],
        "gold": gold,
        "approval_status": "APPROVED_FOR_D2",
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "previous_benchmark_predictions_used_for_gold": False,
    }


CASES = [
    _case("D2-001", "ANAPHORA", [
        ("a1", "patient", "Sinto ardor no antebraço esquerdo desde cedo."),
        ("a2", "patient", "Essa sensação aumenta quando seguro o celular."),
    ], [_mention("ardor", "symptom.burning", ["a1", "a2"], laterality="left", attribute_provenance={"laterality": ["a1"], "temporality": ["a1"]})]),
    _case("D2-002", "ANAPHORA", [
        ("a1", "patient", "Percebi um peso no peito durante a subida."),
        ("a2", "patient", "Ele sumiu quando parei para descansar."),
    ], [_mention("peso", "symptom.chest_pressure", ["a1", "a2"], temporality="past", attribute_provenance={"temporality": ["a1", "a2"]})]),
    _case("D2-003", "ANAPHORA", [
        ("a1", "patient", "Tenho tremor fino nas mãos."),
        ("a2", "clinician", "Esse achado aparece em repouso?"),
        ("a3", "patient", "Sim, principalmente de madrugada."),
    ], [_mention("tremor", "symptom.tremor", ["a1", "a3"], attribute_provenance={"temporality": ["a1"]})]),

    _case("D2-004", "SPEAKER_TRANSITION", [
        ("b1", "clinician", "A senhora ainda usa enalapril?"),
        ("b2", "patient", "Uso, mas meu marido não usa mais nenhum remédio."),
    ], [_mention("enalapril", "medication.enalapril", ["b1", "b2"], status="active", attribute_provenance={"status": ["b2"]})]),
    _case("D2-005", "SPEAKER_TRANSITION", [
        ("b1", "clinician", "Quem teve diabetes na família?"),
        ("b2", "patient", "Minha avó teve, eu não tenho diabetes."),
    ], [
        _mention("diabetes", "condition.diabetes", ["b1", "b2"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["b2"], "temporality": ["b2"]}),
        _mention("diabetes", "condition.diabetes", ["b2"], occurrence=1, negated=True, experiencer="patient", attribute_provenance={"negated": ["b2"], "experiencer": ["b2"]}),
    ]),
    _case("D2-006", "SPEAKER_TRANSITION", [
        ("b1", "patient", "Minha irmã sente falta de ar à noite."),
        ("b2", "clinician", "E você sente falta de ar também?"),
        ("b3", "patient", "Eu não sinto."),
    ], [
        _mention("falta de ar", "symptom.dyspnea", ["b1"], experiencer="family", attribute_provenance={"experiencer": ["b1"]}),
        _mention("falta de ar", "symptom.dyspnea", ["b2", "b3"], occurrence=1, negated=True, experiencer="patient", attribute_provenance={"negated": ["b3"], "experiencer": ["b3"]}),
    ]),

    _case("D2-007", "DISTRIBUTED_TEMPORALITY", [
        ("c1", "patient", "A enxaqueca está controlada nesta semana."),
        ("c2", "patient", "A última crise foi no feriado de junho."),
    ], [_mention("enxaqueca", "condition.migraine", ["c1", "c2"], temporality="current", attribute_provenance={"temporality": ["c1"]})]),
    _case("D2-008", "DISTRIBUTED_TEMPORALITY", [
        ("c1", "patient", "Tive uma queda na cozinha."),
        ("c2", "patient", "Isso aconteceu no começo do ano e não voltou."),
    ], [_mention("queda", "event.fall", ["c1", "c2"], temporality="past", attribute_provenance={"temporality": ["c2"]})]),
    _case("D2-009", "DISTRIBUTED_TEMPORALITY", [
        ("c1", "patient", "A tosse começou na semana retrasada."),
        ("c2", "clinician", "Ela continua hoje?"),
        ("c3", "patient", "Continua, só que mais leve."),
    ], [_mention("tosse", "symptom.cough", ["c1", "c3"], temporality="current", attribute_provenance={"temporality": ["c3"]})]),

    _case("D2-010", "MEDICATION_RECONCILIATION", [
        ("d1", "patient", "Na receita antiga constava losartana de 50 mg."),
        ("d2", "patient", "Depois da internação ficou 25 mg por comprimido."),
    ], [_mention("losartana", "medication.losartan", ["d1", "d2"], dose="25 mg", dose_value="25", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "50 mg"}], attribute_provenance={"dose": ["d2"], "dose_value": ["d2"], "dose_unit": ["d2"], "status": ["d2"]}, relation_provenance={"CHANGED_FROM": ["d2"]})]),
    _case("D2-011", "MEDICATION_RECONCILIATION", [
        ("d1", "patient", "A lista trazia metformina."),
        ("d2", "clinician", "Ela continua na prescrição?"),
        ("d3", "patient", "Não, foi suspensa na consulta passada."),
    ], [_mention("metformina", "medication.metformin", ["d1", "d3"], status="discontinued", temporality="current", relations=[{"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"}], attribute_provenance={"status": ["d3"], "temporality": ["d3"]}, relation_provenance={"DISCONTINUED_AT": ["d3"]})]),
    _case("D2-012", "MEDICATION_RECONCILIATION", [
        ("d1", "patient", "A dipirona está na minha lista de uso."),
        ("d2", "clinician", "Ela segue ativa?"),
        ("d3", "patient", "Sim, sem mudança."),
    ], [_mention("dipirona", "medication.dipyrone", ["d1", "d3"], status="active", attribute_provenance={"status": ["d3"]})]),

    _case("D2-013", "DOSE_TRANSITION", [
        ("e1", "patient", "A prednisona estava em 20 mg."),
        ("e2", "patient", "Agora está em 10 mg por dia."),
    ], [_mention("prednisona", "medication.prednisone", ["e1", "e2"], dose="10 mg", dose_value="10", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "20 mg"}], attribute_provenance={"dose": ["e2"], "dose_value": ["e2"], "dose_unit": ["e2"], "status": ["e2"]}, relation_provenance={"CHANGED_FROM": ["e2"]})]),
    _case("D2-014", "DOSE_TRANSITION", [
        ("e1", "clinician", "Qual dose de sertralina você usa?"),
        ("e2", "patient", "Era 50 mg; desde o retorno, 75 mg."),
    ], [_mention("sertralina", "medication.sertraline", ["e1", "e2"], dose="75 mg", dose_value="75", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "50 mg"}], attribute_provenance={"dose": ["e2"], "dose_value": ["e2"], "dose_unit": ["e2"], "status": ["e2"]}, relation_provenance={"CHANGED_FROM": ["e2"]})]),
    _case("D2-015", "DOSE_TRANSITION", [
        ("e1", "patient", "O adesivo era de 14 mg."),
        ("e2", "patient", "No mês seguinte passei para 7 mg."),
    ], [_mention("adesivo", "medication.patch", ["e1", "e2"], dose="7 mg", dose_value="7", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "14 mg"}], attribute_provenance={"dose": ["e2"], "dose_value": ["e2"], "dose_unit": ["e2"], "status": ["e2"]}, relation_provenance={"CHANGED_FROM": ["e2"]})]),

    _case("D2-016", "FREQUENCY_TRANSITION", [
        ("f1", "patient", "Eu tomava a bombinha duas vezes ao dia."),
        ("f2", "patient", "Com a melhora, reduzi para uma vez ao dia."),
    ], [_mention("bombinha", "medication.inhaler", ["f1", "f2"], frequency="uma vez ao dia", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "duas vezes ao dia"}], attribute_provenance={"frequency": ["f2"], "status": ["f2"]}, relation_provenance={"CHANGED_FROM": ["f2"]})]),
    _case("D2-017", "FREQUENCY_TRANSITION", [
        ("f1", "patient", "A levotiroxina era tomada pela manhã."),
        ("f2", "clinician", "Mudou o horário?"),
        ("f3", "patient", "Agora tomo à noite."),
    ], [_mention("levotiroxina", "medication.levothyroxine", ["f1", "f3"], frequency="à noite", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "pela manhã"}], attribute_provenance={"frequency": ["f3"], "status": ["f3"]}, relation_provenance={"CHANGED_FROM": ["f3"]})]),
    _case("D2-018", "FREQUENCY_TRANSITION", [
        ("f1", "patient", "Uso ibuprofeno todos os dias."),
        ("f2", "patient", "A orientação nova deixou em dias alternados."),
    ], [_mention("ibuprofeno", "medication.ibuprofen", ["f1", "f2"], frequency="dias alternados", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "todos os dias"}], attribute_provenance={"frequency": ["f2"], "status": ["f2"]}, relation_provenance={"CHANGED_FROM": ["f2"]})]),

    _case("D2-019", "FAMILY_PATIENT_EXPERIENCER", [
        ("g1", "patient", "Meu pai teve câncer de pulmão."),
        ("g2", "clinician", "E você tem algum sintoma?"),
        ("g3", "patient", "Eu tenho apenas tosse agora."),
    ], [
        _mention("câncer", "condition.cancer", ["g1"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["g1"], "temporality": ["g1"]}),
        _mention("tosse", "symptom.cough", ["g3"], experiencer="patient", attribute_provenance={"experiencer": ["g3"]}),
    ]),
    _case("D2-020", "FAMILY_PATIENT_EXPERIENCER", [
        ("g1", "clinician", "Há hipertensão na família?"),
        ("g2", "patient", "Minha mãe tem, eu não tenho pressão alta."),
    ], [
        _mention("hipertensão", "condition.hypertension", ["g1", "g2"], experiencer="family", attribute_provenance={"experiencer": ["g2"]}),
        _mention("pressão alta", "condition.hypertension", ["g2"], negated=True, experiencer="patient", attribute_provenance={"negated": ["g2"], "experiencer": ["g2"]}),
    ]),
    _case("D2-021", "FAMILY_PATIENT_EXPERIENCER", [
        ("g1", "patient", "Meu irmão tem asma desde criança."),
        ("g2", "patient", "Eu não tenho chiado."),
    ], [
        _mention("asma", "condition.asthma", ["g1"], experiencer="family", temporality="current", attribute_provenance={"experiencer": ["g1"]}),
        _mention("chiado", "symptom.wheezing", ["g2"], negated=True, experiencer="patient", attribute_provenance={"negated": ["g2"], "experiencer": ["g2"]}),
    ]),

    _case("D2-022", "NEGATION_REVERSAL", [
        ("h1", "patient", "Eu não tinha tontura."),
        ("h2", "patient", "Corrigindo, tive tontura ontem ao levantar."),
    ], [_mention("tontura", "symptom.dizziness", ["h1", "h2"], negated=False, temporality="past", attribute_provenance={"negated": ["h2"], "temporality": ["h2"]})]),
    _case("D2-023", "NEGATION_REVERSAL", [
        ("h1", "clinician", "Você tem náusea?"),
        ("h2", "patient", "Não; pensando bem, tive náusea hoje cedo."),
    ], [_mention("náusea", "symptom.nausea", ["h1", "h2"], negated=False, temporality="past", attribute_provenance={"negated": ["h2"], "temporality": ["h2"]})]),
    _case("D2-024", "NEGATION_REVERSAL", [
        ("h1", "patient", "Não senti dor no trajeto."),
        ("h2", "patient", "Na verdade, senti dor quando cheguei."),
    ], [_mention("dor", "symptom.pain", ["h1", "h2"], negated=False, temporality="past", attribute_provenance={"negated": ["h2"], "temporality": ["h2"]})]),

    _case("D2-025", "TOPIC_SWITCH", [
        ("i1", "patient", "A dor lombar melhorou depois do repouso."),
        ("i2", "patient", "Mudando de assunto, o estômago queima após o almoço."),
    ], [
        _mention("dor lombar", "symptom.back_pain", ["i1"], temporality="past", attribute_provenance={"temporality": ["i1"]}),
        _mention("estômago", "anatomical.stomach", ["i2"]),
    ]),
    _case("D2-026", "TOPIC_SWITCH", [
        ("i1", "patient", "A amlodipina segue em 5 mg."),
        ("i2", "patient", "Sobre a pele, a coceira aparece no pescoço."),
    ], [
        _mention("amlodipina", "medication.amlodipine", ["i1"], dose="5 mg", dose_value="5", dose_unit="mg", status="active", attribute_provenance={"dose": ["i1"], "dose_value": ["i1"], "dose_unit": ["i1"], "status": ["i1"]}),
        _mention("coceira", "symptom.itching", ["i2"]),
    ]),
    _case("D2-027", "TOPIC_SWITCH", [
        ("i1", "clinician", "Vamos encerrar o assunto da glicose."),
        ("i2", "patient", "Falando da visão, vejo pontos brilhantes à noite."),
    ], [
        _mention("glicose", "condition.hyperglycemia", ["i1"]),
        _mention("pontos brilhantes", "symptom.visual_photopsia", ["i2"], temporality="current", attribute_provenance={"temporality": ["i2"]}),
    ]),

    _case("D2-028", "ELLIPTICAL_ANSWER", [
        ("j1", "clinician", "Qual é a dose da metformina?"),
        ("j2", "patient", "Oitocentos e cinquenta miligramas."),
    ], [_mention("metformina", "medication.metformin", ["j1", "j2"], dose="850 mg", dose_value="850", dose_unit="mg", status="active", attribute_provenance={"dose": ["j2"], "dose_value": ["j2"], "dose_unit": ["j2"], "status": ["j1"]})]),
    _case("D2-029", "ELLIPTICAL_ANSWER", [
        ("j1", "clinician", "Em qual lado é a dor do ombro?"),
        ("j2", "patient", "Esquerdo."),
    ], [_mention("dor", "symptom.shoulder_pain", ["j1", "j2"], laterality="left", attribute_provenance={"laterality": ["j2"]})]),
    _case("D2-030", "ELLIPTICAL_ANSWER", [
        ("j1", "clinician", "Você ainda usa o adesivo?"),
        ("j2", "patient", "Parei no mês passado."),
    ], [_mention("adesivo", "medication.patch", ["j1", "j2"], status="discontinued", temporality="current", relations=[{"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"}], attribute_provenance={"status": ["j2"], "temporality": ["j2"]}, relation_provenance={"DISCONTINUED_AT": ["j2"]})]),

    _case("D2-031", "CLINICIAN_CORRECTION", [
        ("k1", "clinician", "O prontuário registra hipertensão confirmada."),
        ("k2", "clinician", "Corrigindo: era apenas uma suspeita."),
    ], [_mention("hipertensão", "condition.hypertension", ["k1", "k2"], certainty="possible", attribute_provenance={"certainty": ["k2"]})]),
    _case("D2-032", "CLINICIAN_CORRECTION", [
        ("k1", "clinician", "A cirurgia ocorreu em fevereiro."),
        ("k2", "clinician", "Retifico: foi em março."),
    ], [_mention("cirurgia", "procedure.surgery", ["k1", "k2"], temporality="past", attribute_provenance={"temporality": ["k2"]})]),
    _case("D2-033", "CLINICIAN_CORRECTION", [
        ("k1", "clinician", "A lesão fica no joelho direito."),
        ("k2", "clinician", "A anotação correta é joelho esquerdo."),
    ], [_mention("lesão", "condition.lesion", ["k1", "k2"], laterality="left", attribute_provenance={"laterality": ["k2"]})]),

    _case("D2-034", "PATIENT_SELF_CORRECTION", [
        ("l1", "patient", "Minha mãe teve asma."),
        ("l2", "patient", "Não, pensando bem foi minha tia."),
    ], [_mention("asma", "condition.asthma", ["l1", "l2"], experiencer="family", temporality="past", attribute_provenance={"experiencer": ["l2"], "temporality": ["l1"]})]),
    _case("D2-035", "PATIENT_SELF_CORRECTION", [
        ("l1", "patient", "Tomo atenolol à noite."),
        ("l2", "patient", "Corrijo: tomo pela manhã."),
    ], [_mention("atenolol", "medication.atenolol", ["l1", "l2"], frequency="pela manhã", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "à noite"}], attribute_provenance={"frequency": ["l2"], "status": ["l1"]}, relation_provenance={"CHANGED_FROM": ["l2"]})]),
    _case("D2-036", "PATIENT_SELF_CORRECTION", [
        ("l1", "patient", "O exame mostrou anemia."),
        ("l2", "patient", "Melhor dizendo, mostrou ferro baixo."),
    ], [_mention("anemia", "condition.anemia", ["l1", "l2"], certainty="possible", attribute_provenance={"certainty": ["l2"]})]),
]


def _validate_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    ids = [record["case_id"] for record in records]
    if len(records) != 36:
        errors.append(f"expected 36 cases, found {len(records)}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate case ids")
    families = {record["scenario_family"] for record in records}
    expected_families = {"ANAPHORA", "SPEAKER_TRANSITION", "DISTRIBUTED_TEMPORALITY", "MEDICATION_RECONCILIATION", "DOSE_TRANSITION", "FREQUENCY_TRANSITION", "FAMILY_PATIENT_EXPERIENCER", "NEGATION_REVERSAL", "TOPIC_SWITCH", "ELLIPTICAL_ANSWER", "CLINICIAN_CORRECTION", "PATIENT_SELF_CORRECTION"}
    if families != expected_families:
        errors.append(f"family coverage mismatch: {sorted(expected_families - families)}")
    for record in records:
        segment_ids = {segment["segment_id"] for segment in record["segments"]}
        if not record["gold"]:
            errors.append(f"{record['case_id']}: no gold")
        if record["resolver_used_for_gold"] or record["runtime_predictions_used_for_gold"] or record["previous_benchmark_predictions_used_for_gold"]:
            errors.append(f"{record['case_id']}: prediction contamination flag")
        for mention in record["gold"]:
            occurrences = record["text"].casefold().count(mention["surface"].casefold())
            if occurrences <= mention.get("occurrence", 0):
                errors.append(f"{record['case_id']}: occurrence out of range for {mention['surface']!r}")
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
    known_texts: dict[str, str] = {}
    compared: list[str] = []
    for path in sorted(DATA.glob("*.jsonl")) + sorted(DATA.glob("*.json")):
        if path == OUTPUT:
            continue
        compared.append(str(path))
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line in content.splitlines():
            if not line.strip() or not line.lstrip().startswith("{"):
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict) and item.get("text"):
                known_texts[_normalize(item["text"])] = str(path)
    collisions = [
        {"case_id": record["case_id"], "source": known_texts[_normalize(record["text"])]}
        for record in records
        if _normalize(record["text"]) in known_texts
    ]
    return {
        "status": "PASS" if not collisions else "FAIL",
        "candidate_cases": len(records),
        "compared_corpus_files": compared,
        "exact_normalized_text_collisions": collisions,
        "collision_count": len(collisions),
        "comparison_scope": "V3-V7, consumed holdouts, D1 and other benchmark JSON/JSONL data files",
    }


def main() -> None:
    errors = _validate_records(CASES)
    if errors:
        raise RuntimeError("D2 validation failed: " + "; ".join(errors))
    disjointness = _disjointness(CASES)
    if disjointness["status"] != "PASS":
        raise RuntimeError(f"D2 disjointness failed: {disjointness['exact_normalized_text_collisions']}")
    DATA.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in CASES), encoding="utf-8")
    DISJOINTNESS.write_text(json.dumps(disjointness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "status": "D2_FROZEN",
        "benchmark": "D2 Unseen Diagnostic Generalization",
        "official_corpus": str(OUTPUT),
        "official_corpus_checksum": _sha256(OUTPUT),
        "policy_version": POLICY_VERSION,
        "policy_checksum": _sha256(POLICY),
        "case_count": len(CASES),
        "mention_count": sum(len(record["gold"]) for record in CASES),
        "scenario_families": sorted({record["scenario_family"] for record in CASES}),
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "previous_benchmark_predictions_used_for_gold": False,
        "trace_schema": "clinical-evaluation-trace/v2",
        "trace_v2_frozen": True,
        "disjointness": str(DISJOINTNESS),
        "disjointness_status": disjointness["status"],
        "one_shot_authorized": True,
        "one_shot_run_count": 0,
        "resolver_repair_after_run": "NOT_AUTHORIZED",
        "d1": "CONSUMED_IMMUTABLE",
        "v7": "CONSUMED_IMMUTABLE",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
