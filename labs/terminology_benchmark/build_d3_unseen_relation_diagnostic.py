"""Build and freeze the unseen D3 relation generalization diagnostic.

This builder contains only human-policy-governed gold. It never imports or
executes the clinical resolver.
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
OUTPUT = DATA / "d3_relation_generalization_official.jsonl"
MANIFEST = RESULTS / "D3_FREEZE_MANIFEST.json"
DISJOINTNESS = RESULTS / "d3-disjointness-report-2026-08-15.json"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
COMPILER = ROOT / "clinical_projection.py"
TRACE_SCHEMA = ROOT / "evaluation_trace.py"
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
    value: dict[str, Any] = {
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
    value.update(attributes)
    return value


def _case(case_id: str, family: str, segments: list[tuple[str, str, str]], gold: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "text": "\n".join(f"{speaker}: {text}" for _, speaker, text in segments),
        "language": "pt-BR",
        "source": "niede-d3-relation-generalization",
        "policy_version": POLICY_VERSION,
        "scenario_family": family,
        "segments": [{"segment_id": sid, "speaker": speaker, "text": text} for sid, speaker, text in segments],
        "gold": gold,
        "approval_status": "APPROVED_FOR_D3",
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "previous_benchmark_predictions_used_for_gold": False,
    }


CASES = [
    # Dose relations: six new medication contexts, including elliptical and
    # cross-segment answers.
    _case("D3-001", "DOSE_RELATION", [("q1", "clinician", "Qual a dose da carvedilol após o jantar?"), ("q2", "patient", "Duas cápsulas de 6,25 mg." )], [_mention("carvedilol", "medication.carvedilol", ["q1", "q2"], dose="6.25 mg", dose_value="6.25", dose_unit="mg", status="active", attribute_provenance={"dose": ["q2"], "dose_value": ["q2"], "dose_unit": ["q2"], "status": ["q2"]}, relation_provenance={"HAS_DOSE": ["q2"]})]),
    _case("D3-002", "DOSE_RELATION", [("q1", "patient", "A cápsula de venlafaxina ficou menor na troca."), ("q2", "patient", "Agora é de 37,5 mg pela manhã." )], [_mention("venlafaxina", "medication.venlafaxine", ["q1", "q2"], dose="37.5 mg", dose_value="37.5", dose_unit="mg", status="active", attribute_provenance={"dose": ["q2"], "dose_value": ["q2"], "dose_unit": ["q2"], "status": ["q2"]}, relation_provenance={"HAS_DOSE": ["q2"]})]),
    _case("D3-003", "DOSE_RELATION", [("q1", "clinician", "A receita menciona lamotrigina."), ("q2", "patient", "Tomo 100 mg no horário do almoço." )], [_mention("lamotrigina", "medication.lamotrigine", ["q1", "q2"], dose="100 mg", dose_value="100", dose_unit="mg", status="active", attribute_provenance={"dose": ["q2"], "dose_value": ["q2"], "dose_unit": ["q2"], "status": ["q2"]}, relation_provenance={"HAS_DOSE": ["q2"]})]),
    _case("D3-004", "DOSE_RELATION", [("q1", "patient", "Uso a solução de levodopa em casa."), ("q2", "clinician", "E qual medida você coloca?"), ("q3", "patient", "São 2,5 ml por tomada." )], [_mention("levodopa", "medication.levodopa", ["q1", "q3"], dose="2.5 ml", dose_value="2.5", dose_unit="ml", status="active", attribute_provenance={"dose": ["q3"], "dose_value": ["q3"], "dose_unit": ["q3"], "status": ["q3"]}, relation_provenance={"HAS_DOSE": ["q3"]})]),
    _case("D3-005", "DOSE_RELATION", [("q1", "patient", "A nortriptilina segue na caixa azul."), ("q2", "patient", "A etiqueta mostra 25 mg, sem alteração." )], [_mention("nortriptilina", "medication.nortriptyline", ["q1", "q2"], dose="25 mg", dose_value="25", dose_unit="mg", status="active", attribute_provenance={"dose": ["q2"], "dose_value": ["q2"], "dose_unit": ["q2"], "status": ["q2"]}, relation_provenance={"HAS_DOSE": ["q2"]})]),
    _case("D3-006", "DOSE_RELATION", [("q1", "clinician", "O anticoagulante apixabana aparece no plano."), ("q2", "patient", "Uso 5 mg em cada tomada." )], [_mention("apixabana", "medication.apixaban", ["q1", "q2"], dose="5 mg", dose_value="5", dose_unit="mg", status="active", attribute_provenance={"dose": ["q2"], "dose_value": ["q2"], "dose_unit": ["q2"], "status": ["q2"]}, relation_provenance={"HAS_DOSE": ["q2"]})]),

    # Frequency relations use distinct lexical cues and ownership contexts.
    _case("D3-007", "FREQUENCY_RELATION", [("f1", "patient", "A duloxetina eu tomo ao acordar." )], [_mention("duloxetina", "medication.duloxetine", ["f1"], frequency="ao acordar", status="active", attribute_provenance={"frequency": ["f1"], "status": ["f1"]}, relation_provenance={"HAS_FREQUENCY": ["f1"]})]),
    _case("D3-008", "FREQUENCY_RELATION", [("f1", "clinician", "O colírio de timolol é usado como?"), ("f2", "patient", "Uma gota de oito em oito horas." )], [_mention("timolol", "medication.timolol", ["f1", "f2"], frequency="de oito em oito horas", status="active", attribute_provenance={"frequency": ["f2"], "status": ["f2"]}, relation_provenance={"HAS_FREQUENCY": ["f2"]})]),
    _case("D3-009", "FREQUENCY_RELATION", [("f1", "patient", "O carbonato de lítio ficou na rotina da noite."), ("f2", "patient", "Tomo antes de dormir." )], [_mention("carbonato de lítio", "medication.lithium", ["f1", "f2"], frequency="antes de dormir", status="active", attribute_provenance={"frequency": ["f2"], "status": ["f2"]}, relation_provenance={"HAS_FREQUENCY": ["f2"]})]),
    _case("D3-010", "FREQUENCY_RELATION", [("f1", "patient", "A rivaroxabana fica para depois do jantar." )], [_mention("rivaroxabana", "medication.rivaroxaban", ["f1"], frequency="depois do jantar", status="active", attribute_provenance={"frequency": ["f1"], "status": ["f1"]}, relation_provenance={"HAS_FREQUENCY": ["f1"]})]),
    _case("D3-011", "FREQUENCY_RELATION", [("f1", "patient", "A vitamina D entra aos domingos."), ("f2", "clinician", "Mantenha esse intervalo." )], [_mention("vitamina D", "medication.vitamin_d", ["f1", "f2"], frequency="aos domingos", status="active", attribute_provenance={"frequency": ["f1"], "status": ["f2"]}, relation_provenance={"HAS_FREQUENCY": ["f1"]})]),
    _case("D3-012", "FREQUENCY_RELATION", [("f1", "clinician", "A cefalexina foi mantida."), ("f2", "patient", "Ficou de 12 em 12 horas." )], [_mention("cefalexina", "medication.cephalexin", ["f1", "f2"], frequency="de 12 em 12 horas", status="active", attribute_provenance={"frequency": ["f2"], "status": ["f1"]}, relation_provenance={"HAS_FREQUENCY": ["f2"]})]),

    # Laterality relations: symptom ownership must survive the surrounding text.
    _case("D3-013", "LATERALITY_RELATION", [("l1", "patient", "A dormência apareceu no braço esquerdo." )], [_mention("dormência", "symptom.numbness", ["l1"], laterality="left", attribute_provenance={"laterality": ["l1"]}, relation_provenance={"HAS_LATERALITY": ["l1"]})]),
    _case("D3-014", "LATERALITY_RELATION", [("l1", "patient", "A pontada no tornozelo direito voltou ao caminhar." )], [_mention("pontada", "symptom.stabbing_pain", ["l1"], laterality="right", attribute_provenance={"laterality": ["l1"]}, relation_provenance={"HAS_LATERALITY": ["l1"]})]),
    _case("D3-015", "LATERALITY_RELATION", [("l1", "clinician", "A queimação fica de que lado?"), ("l2", "patient", "Do lado esquerdo, perto da costela." )], [_mention("queimação", "symptom.burning", ["l1", "l2"], laterality="left", attribute_provenance={"laterality": ["l2"]}, relation_provenance={"HAS_LATERALITY": ["l2"]})]),
    _case("D3-016", "LATERALITY_RELATION", [("l1", "patient", "O formigamento migrou para a mão direita."), ("l2", "patient", "É só nesse lado." )], [_mention("formigamento", "symptom.tingling", ["l1", "l2"], laterality="right", attribute_provenance={"laterality": ["l1", "l2"]}, relation_provenance={"HAS_LATERALITY": ["l1"]})]),
    _case("D3-017", "LATERALITY_RELATION", [("l1", "patient", "A dor na panturrilha esquerda piora à tarde."), ("l2", "clinician", "Entendi, somente a esquerda." )], [_mention("dor", "symptom.pain", ["l1", "l2"], laterality="left", attribute_provenance={"laterality": ["l1", "l2"]}, relation_provenance={"HAS_LATERALITY": ["l1"]})]),
    _case("D3-018", "LATERALITY_RELATION", [("l1", "patient", "O tremor fica mais forte na mão direita durante o café."), ("l2", "patient", "No repouso ainda é desse lado." )], [_mention("tremor", "symptom.tremor", ["l1", "l2"], laterality="right", attribute_provenance={"laterality": ["l1", "l2"]}, relation_provenance={"HAS_LATERALITY": ["l1"]})]),

    # Explicit transitions: current value plus a separate CHANGED_FROM signal.
    _case("D3-019", "TRANSITION_RELATION", [("t1", "patient", "A dose de escitalopram era 10 mg."), ("t2", "patient", "Depois passou para 15 mg." )], [_mention("escitalopram", "medication.escitalopram", ["t1", "t2"], dose="15 mg", dose_value="15", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "10 mg"}], attribute_provenance={"dose": ["t2"], "dose_value": ["t2"], "dose_unit": ["t2"], "status": ["t2"]}, relation_provenance={"CHANGED_FROM": ["t2"]})]),
    _case("D3-020", "TRANSITION_RELATION", [("t1", "patient", "O inalador era usado três vezes ao dia."), ("t2", "patient", "Agora fica duas vezes ao dia." )], [_mention("inalador", "medication.inhaler", ["t1", "t2"], frequency="duas vezes ao dia", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "três vezes ao dia"}], attribute_provenance={"frequency": ["t2"], "status": ["t2"]}, relation_provenance={"CHANGED_FROM": ["t2"]})]),
    _case("D3-021", "TRANSITION_RELATION", [("t1", "clinician", "O adesivo de nicotina estava em 21 mg."), ("t2", "patient", "Na semana seguinte, ficou em 14 mg." )], [_mention("adesivo de nicotina", "medication.nicotine_patch", ["t1", "t2"], dose="14 mg", dose_value="14", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "21 mg"}], attribute_provenance={"dose": ["t2"], "dose_value": ["t2"], "dose_unit": ["t2"], "status": ["t2"]}, relation_provenance={"CHANGED_FROM": ["t2"]})]),
    _case("D3-022", "TRANSITION_RELATION", [("t1", "patient", "Eu tomava a levotiroxina de manhã."), ("t2", "patient", "Com a orientação nova, passei para a noite." )], [_mention("levotiroxina", "medication.levothyroxine", ["t1", "t2"], frequency="à noite", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "de manhã"}], attribute_provenance={"frequency": ["t2"], "status": ["t2"]}, relation_provenance={"CHANGED_FROM": ["t2"]})]),
    _case("D3-023", "TRANSITION_RELATION", [("t1", "patient", "A prednisolona estava em 40 mg."), ("t2", "clinician", "Hoje o esquema é 20 mg." )], [_mention("prednisolona", "medication.prednisolone", ["t1", "t2"], dose="20 mg", dose_value="20", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "40 mg"}], attribute_provenance={"dose": ["t2"], "dose_value": ["t2"], "dose_unit": ["t2"], "status": ["t2"]}, relation_provenance={"CHANGED_FROM": ["t2"]})]),
    _case("D3-024", "TRANSITION_RELATION", [("t1", "patient", "A frequência da gabapentina era à noite."), ("t2", "patient", "Na alta, ficou pela manhã." )], [_mention("gabapentina", "medication.gabapentin", ["t1", "t2"], frequency="pela manhã", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "frequency", "value": "à noite"}], attribute_provenance={"frequency": ["t2"], "status": ["t2"]}, relation_provenance={"CHANGED_FROM": ["t2"]})]),

    # Current versus historical: historical context must not become current
    # attribute ownership or a current relation.
    _case("D3-025", "CURRENT_HISTORICAL", [("h1", "patient", "Usei amoxicilina no inverno passado."), ("h2", "patient", "Hoje não estou usando antibiótico." )], [_mention("amoxicilina", "medication.amoxicillin", ["h1"], temporality="past", status=None, attribute_provenance={"temporality": ["h1"]})]),
    _case("D3-026", "CURRENT_HISTORICAL", [("h1", "patient", "A antiga dose de sertralina era 50 mg."), ("h2", "patient", "A atual é 75 mg." )], [_mention("sertralina", "medication.sertraline", ["h1", "h2"], dose="75 mg", dose_value="75", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "50 mg"}], attribute_provenance={"dose": ["h2"], "dose_value": ["h2"], "dose_unit": ["h2"], "status": ["h2"]}, relation_provenance={"CHANGED_FROM": ["h2"]})]),
    _case("D3-027", "CURRENT_HISTORICAL", [("h1", "patient", "A dor no joelho apareceu ontem."), ("h2", "patient", "Agora está ausente." )], [_mention("dor", "symptom.pain", ["h1", "h2"], temporality="past", attribute_provenance={"temporality": ["h1", "h2"]})]),
    _case("D3-028", "CURRENT_HISTORICAL", [("h1", "patient", "A cirurgia de catarata foi em março."), ("h2", "patient", "A visão está melhor hoje." )], [_mention("cirurgia", "procedure.cataract_surgery", ["h1"], temporality="past", attribute_provenance={"temporality": ["h1"]})]),
    _case("D3-029", "CURRENT_HISTORICAL", [("h1", "patient", "Parei a hidroclorotiazida no mês passado."), ("h2", "clinician", "Então ela permanece suspensa." )], [_mention("hidroclorotiazida", "medication.hydrochlorothiazide", ["h1", "h2"], status="discontinued", temporality="current", relations=[{"relation_type": "DISCONTINUED_AT", "target": "status", "value": "discontinued"}], attribute_provenance={"status": ["h1", "h2"], "temporality": ["h1"]}, relation_provenance={"DISCONTINUED_AT": ["h1"]})]),
    _case("D3-030", "CURRENT_HISTORICAL", [("h1", "patient", "Tive uma crise de asma na adolescência."), ("h2", "patient", "Hoje respiro sem chiado." )], [_mention("crise de asma", "event.asthma_attack", ["h1"], temporality="past", attribute_provenance={"temporality": ["h1"]})]),

    # Ownership/provenance: relation evidence must remain attached to the
    # correct mention when adjacent entities are present.
    _case("D3-031", "PROVENANCE_OWNERSHIP", [("p1", "patient", "Tomo enalapril 10 mg e atenolol 25 mg."), ("p2", "patient", "O primeiro é pela manhã; o segundo, à noite." )], [_mention("enalapril", "medication.enalapril", ["p1", "p2"], dose="10 mg", dose_value="10", dose_unit="mg", frequency="pela manhã", status="active", attribute_provenance={"dose": ["p1"], "dose_value": ["p1"], "dose_unit": ["p1"], "frequency": ["p2"], "status": ["p1"]}, relation_provenance={"HAS_DOSE": ["p1"], "HAS_FREQUENCY": ["p2"]}), _mention("atenolol", "medication.atenolol", ["p1", "p2"], dose="25 mg", dose_value="25", dose_unit="mg", frequency="à noite", status="active", attribute_provenance={"dose": ["p1"], "dose_value": ["p1"], "dose_unit": ["p1"], "frequency": ["p2"], "status": ["p1"]}, relation_provenance={"HAS_DOSE": ["p1"], "HAS_FREQUENCY": ["p2"]})]),
    _case("D3-032", "PROVENANCE_OWNERSHIP", [("p1", "patient", "A dor no ombro e a dormência na mão aparecem juntas."), ("p2", "patient", "A dor é do lado direito, mas a dormência fica à esquerda." )], [_mention("dor", "symptom.pain", ["p1", "p2"], laterality="right", attribute_provenance={"laterality": ["p2"]}, relation_provenance={"HAS_LATERALITY": ["p2"]}), _mention("dormência", "symptom.numbness", ["p1", "p2"], laterality="left", attribute_provenance={"laterality": ["p2"]}, relation_provenance={"HAS_LATERALITY": ["p2"]})]),
    _case("D3-033", "PROVENANCE_OWNERSHIP", [("p1", "patient", "Uso metformina 500 mg e sitagliptina 100 mg."), ("p2", "clinician", "A metformina ficou na dose menor; a outra não mudou." )], [_mention("metformina", "medication.metformin", ["p1", "p2"], dose="500 mg", dose_value="500", dose_unit="mg", status="active", attribute_provenance={"dose": ["p1"], "dose_value": ["p1"], "dose_unit": ["p1"], "status": ["p1"]}, relation_provenance={"HAS_DOSE": ["p1"]}), _mention("sitagliptina", "medication.sitagliptin", ["p1", "p2"], dose="100 mg", dose_value="100", dose_unit="mg", status="active", attribute_provenance={"dose": ["p1"], "dose_value": ["p1"], "dose_unit": ["p1"], "status": ["p1"]}, relation_provenance={"HAS_DOSE": ["p1"]})]),
    _case("D3-034", "PROVENANCE_OWNERSHIP", [("p1", "clinician", "A mãe relata dor no quadril; o paciente relata tosse."), ("p2", "patient", "A tosse é do lado direito? Não, é só irritação." )], [_mention("dor", "symptom.pain", ["p1"], experiencer="family", attribute_provenance={"experiencer": ["p1"]}), _mention("tosse", "symptom.cough", ["p1", "p2"], experiencer="patient", attribute_provenance={"experiencer": ["p1", "p2"]})]),
    _case("D3-035", "PROVENANCE_OWNERSHIP", [("p1", "patient", "A receita trazia losartana 50 mg."), ("p2", "patient", "A partir de ontem, a losartana ficou em 25 mg; a sinvastatina segue igual." )], [_mention("losartana", "medication.losartan", ["p1", "p2"], dose="25 mg", dose_value="25", dose_unit="mg", status="active", relations=[{"relation_type": "CHANGED_FROM", "target": "dose", "value": "50 mg"}], attribute_provenance={"dose": ["p2"], "dose_value": ["p2"], "dose_unit": ["p2"], "status": ["p2"]}, relation_provenance={"CHANGED_FROM": ["p2"]}), _mention("sinvastatina", "medication.simvastatin", ["p2"], status="active", attribute_provenance={"status": ["p2"]})]),
    _case("D3-036", "PROVENANCE_OWNERSHIP", [("p1", "patient", "Tenho formigamento no lado esquerdo e tomo pregabalina."), ("p2", "patient", "A pregabalina é 75 mg à noite; o lado não mudou." )], [_mention("formigamento", "symptom.tingling", ["p1", "p2"], laterality="left", attribute_provenance={"laterality": ["p1", "p2"]}, relation_provenance={"HAS_LATERALITY": ["p1"]}), _mention("pregabalina", "medication.pregabalin", ["p1", "p2"], dose="75 mg", dose_value="75", dose_unit="mg", frequency="à noite", status="active", attribute_provenance={"dose": ["p2"], "dose_value": ["p2"], "dose_unit": ["p2"], "frequency": ["p2"], "status": ["p1", "p2"]}, relation_provenance={"HAS_DOSE": ["p2"], "HAS_FREQUENCY": ["p2"]})]),
]


def _validate(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if len(records) != 36:
        errors.append(f"expected 36 cases, found {len(records)}")
    ids = [item["case_id"] for item in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate case ids")
    counts: dict[str, int] = {}
    for record in records:
        counts[record["scenario_family"]] = counts.get(record["scenario_family"], 0) + 1
        segment_ids = {segment["segment_id"] for segment in record["segments"]}
        if not record["gold"]:
            errors.append(f"{record['case_id']}: missing gold")
        for mention in record["gold"]:
            if _normalize(mention["surface"]) not in _normalize(record["text"]):
                errors.append(f"{record['case_id']}: missing surface {mention['surface']}")
            if not set(mention["segment_ids"]).issubset(segment_ids):
                errors.append(f"{record['case_id']}: invalid segment ownership")
            for source_map in (mention.get("attribute_provenance", {}), mention.get("relation_provenance", {})):
                for source_ids in source_map.values():
                    if not set(source_ids).issubset(segment_ids):
                        errors.append(f"{record['case_id']}: invalid provenance")
        if record["resolver_used_for_gold"] or record["runtime_predictions_used_for_gold"] or record["previous_benchmark_predictions_used_for_gold"]:
            errors.append(f"{record['case_id']}: prediction contamination flag")
    if set(counts.values()) != {6} or len(counts) != 6:
        errors.append(f"family distribution mismatch: {counts}")
    return errors


def _candidate_texts() -> list[Path]:
    paths = list((ROOT / "data").glob("*.jsonl")) + list((ROOT / "data").glob("*.json"))
    paths += list((ROOT / "results").glob("*.json"))
    paths += [ROOT / "tests/benchmark/test_relation_compiler.py"] if (ROOT / "tests/benchmark/test_relation_compiler.py").exists() else []
    paths += [ROOT.parent.parent / "tests/benchmark/test_relation_compiler.py"]
    return [path for path in paths if path.exists() and path != OUTPUT]


def _disjointness(records: list[dict[str, Any]]) -> dict[str, Any]:
    collisions: list[dict[str, str]] = []
    compared: list[str] = []
    for path in _candidate_texts():
        content = _normalize(path.read_text(encoding="utf-8", errors="ignore"))
        compared.append(str(path))
        for record in records:
            if _normalize(record["text"]) in content:
                collisions.append({"case_id": record["case_id"], "source": str(path)})
    return {
        "status": "PASS" if not collisions else "FAIL",
        "candidate_cases": len(records),
        "compared_files": compared,
        "exact_normalized_text_collisions": collisions,
        "collision_count": len(collisions),
        "comparison_scope": "V3-V7, D1, D2, consumed holdouts, and compiler synthetic tests",
    }


def main() -> None:
    errors = _validate(CASES)
    if errors:
        raise RuntimeError("D3 validation failed: " + "; ".join(errors))
    disjointness = _disjointness(CASES)
    if disjointness["status"] != "PASS":
        raise RuntimeError(f"D3 disjointness failed: {disjointness['exact_normalized_text_collisions']}")
    DATA.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in CASES), encoding="utf-8")
    DISJOINTNESS.write_text(json.dumps(disjointness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "status": "D3_FROZEN",
        "benchmark": "D3 Relation Generalization Diagnostic",
        "official_corpus": str(OUTPUT),
        "official_corpus_checksum": _sha256(OUTPUT),
        "policy_version": POLICY_VERSION,
        "policy_checksum": _sha256(POLICY),
        "compiler_checksum": _sha256(COMPILER),
        "resolver_config_checksum": hashlib.sha256((str(ROOT / "clinical_projection.py") + _sha256(COMPILER)).encode()).hexdigest(),
        "trace_schema": "clinical-evaluation-trace/v2",
        "trace_schema_checksum": _sha256(TRACE_SCHEMA),
        "case_count": len(CASES),
        "mention_count": sum(len(record["gold"]) for record in CASES),
        "scenario_families": sorted({record["scenario_family"] for record in CASES}),
        "family_distribution": {family: sum(record["scenario_family"] == family for record in CASES) for family in sorted({record["scenario_family"] for record in CASES})},
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "previous_benchmark_predictions_used_for_gold": False,
        "disjointness_report": str(DISJOINTNESS),
        "disjointness_status": disjointness["status"],
        "one_shot_authorized": True,
        "one_shot_run_count": 0,
        "repair_after_run": "NOT_AUTHORIZED",
        "v7": "CONSUMED_IMMUTABLE",
        "d1": "CONSUMED_IMMUTABLE",
        "d2": "CONSUMED_IMMUTABLE",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
