"""Build and freeze the unseen D4 relation-input contract diagnostic.

Gold is authored from the frozen v1.3 policy and explicit semantic contracts.
This module deliberately does not import the resolver or runtime predictions.
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
OUTPUT = DATA / "d4_relation_input_generalization_official.jsonl"
MANIFEST = RESULTS / "D4_FREEZE_MANIFEST.json"
DISJOINTNESS = RESULTS / "d4-disjointness-report-2026-08-15.json"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
COMPILER = ROOT / "clinical_projection.py"
C2_SCHEMA = ROOT.parent.parent / "docs/clinical-conversational-semantics/RELATION_INPUT_SIGNAL_SCHEMA.json"
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


def _signal(
    attribute_type: str,
    value: Any,
    owner_type: str | None,
    state: str,
    status: str,
    source_segment_ids: list[str],
) -> dict[str, Any]:
    return {
        "attribute_type": attribute_type,
        "value": value,
        "owner_type": owner_type,
        "state": state,
        "status": status,
        "source_segment_ids": source_segment_ids,
    }


def _transition(
    attribute_type: str,
    previous_value: Any,
    current_value: Any,
    owner_type: str | None,
    state: str,
    status: str,
    source_segment_ids: list[str],
) -> dict[str, Any]:
    return {
        "attribute_type": attribute_type,
        "previous_value": previous_value,
        "current_value": current_value,
        "owner_type": owner_type,
        "transition_type": "CHANGED_FROM",
        "state": state,
        "status": status,
        "source_segment_ids": source_segment_ids,
    }


def _case(
    case_id: str,
    family: str,
    segments: list[tuple[str, str, str]],
    gold: list[dict[str, Any]],
    signal_gold: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "text": "\n".join(f"{speaker}: {text}" for _, speaker, text in segments),
        "language": "pt-BR",
        "source": "niede-d4-relation-input-generalization",
        "policy_version": POLICY_VERSION,
        "scenario_family": family,
        "segments": [{"segment_id": sid, "speaker": speaker, "text": text} for sid, speaker, text in segments],
        "gold": gold,
        "signal_gold": signal_gold,
        "approval_status": "APPROVED_FOR_D4",
        "gold_generation": "AI_ASSISTED_HUMAN_POLICY_GOVERNED",
        "resolver_used_for_gold": False,
        "runtime_predictions_used_for_gold": False,
        "previous_benchmark_predictions_used_for_gold": False,
    }


CASES: list[dict[str, Any]] = []


def _build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []

    dose_rows = [
        ("losartana", "medication.losartan", "18 mg", "r1", "r2", "A receita separou a losartana do restante.", "A dose confirmada é 18 mg depois do desjejum."),
        ("enalapril", "medication.enalapril", "7,5 mg", "r1", "r3", "O cardiologista manteve enalapril no esquema.", "Na caixa nova, a marcação é de 7,5 mg."),
        ("metformina", "medication.metformin", "850 mg", "r1", "r2", "Metformina aparece no controle da manhã.", "No rótulo consta 850 mg por tomada."),
        ("sertralina", "medication.sertraline", "62,5 mg", "r1", "r3", "Sertralina fica no compartimento azul.", "A etiqueta da sertralina informa 62,5 mg."),
        ("atenolol", "medication.atenolol", "12,5 mg", "r1", "r2", "O atenolol continua na lista domiciliar.", "Para este comprimido, a dose é 12,5 mg."),
        ("amlodipino", "medication.amlodipine", "3 mg", "r1", "r3", "Amlodipino foi citado na conferência.", "A anotação do frasco diz 3 mg."),
    ]
    for index, (surface, concept, dose, first, second, lead, answer) in enumerate(dose_rows, 1):
        value = dose.replace(",", ".").split()[0]
        gold = _mention(surface, concept, [first, second], dose=dose, dose_value=value, dose_unit="mg", status="active", attribute_provenance={"dose": [second], "dose_value": [second], "dose_unit": [second], "status": [first]}, relation_provenance={"HAS_DOSE": [second]})
        cases.append(_case(f"D4-{index:03d}", "OWNER_SENSITIVE_DOSE", [(first, "patient", lead), (second, "patient", answer)], [gold], {"m1": {"attributes": [_signal("dose", dose, "medication", "current", "RESOLVED", [second])], "transitions": []}}))

    frequency_rows = [
        ("dipirona", "medication.dipyrone", "a cada oito horas", "f1", "f2", "Dipirona está ao lado do termômetro.", "Para ela, o intervalo é a cada oito horas."),
        ("ibuprofeno", "medication.ibuprofen", "após o almoço", "f1", "f3", "Ibuprofeno foi listado no papel azul.", "A orientação deste remédio é após o almoço."),
        ("prednisona", "medication.prednisone", "em dias alternados", "f1", "f2", "Prednisona ainda aparece na conciliação.", "A frequência indicada ficou em dias alternados."),
        ("levotiroxina", "medication.levothyroxine", "antes do café", "f1", "f3", "Levotiroxina foi separada dos comprimidos da noite.", "Ela deve ser tomada antes do café."),
        ("enalapril", "medication.enalapril", "duas vezes ao dia", "f1", "f2", "Enalapril é o primeiro medicamento da lista.", "O primeiro fica duas vezes ao dia."),
        ("losartana", "medication.losartan", "aos sábados", "f1", "f3", "Losartana ficou marcada no calendário.", "A anotação final diz aos sábados."),
    ]
    for offset, (surface, concept, frequency, first, second, lead, answer) in enumerate(frequency_rows, 7):
        gold = _mention(surface, concept, [first, second], frequency=frequency, status="active", attribute_provenance={"frequency": [second], "status": [first]}, relation_provenance={"HAS_FREQUENCY": [second]})
        cases.append(_case(f"D4-{offset:03d}", "OWNER_SENSITIVE_FREQUENCY", [(first, "patient", lead), (second, "patient", answer)], [gold], {"m1": {"attributes": [_signal("frequency", frequency, "medication", "current", "RESOLVED", [second])], "transitions": []}}))

    state_rows = [
        ("amoxicilina", "medication.amoxicillin", "s1", "s2", "Usei amoxicilina durante a viagem de abril.", "No momento, não estou usando esse antibiótico.", "past"),
        ("cirurgia", "procedure.cataract_surgery", "s1", "s2", "A cirurgia de catarata aconteceu no início do ano.", "Hoje a recuperação está tranquila.", "past"),
        ("dor", "symptom.pain", "s1", "s2", "A dor surgiu anteontem no ombro.", "Agora não sinto mais dor.", "past"),
        ("tosse", "symptom.cough", "s1", "s2", "A tosse ocorreu na semana da mudança.", "Neste momento, não há tosse.", "past"),
        ("crise", "event.asthma_attack", "s1", "s3", "Tive uma crise de asma na infância.", "Hoje a respiração segue estável.", "past"),
        ("sertralina", "medication.sertraline", "s1", "s3", "A dose anterior da sertralina era 25 mg.", "A atual é 50 mg e sigo usando.", "current"),
    ]
    for offset, (surface, concept, first, second, lead, answer, temporality) in enumerate(state_rows, 13):
        attrs: dict[str, Any] = {"temporality": temporality}
        if surface == "sertralina":
            attrs.update({"dose": "50 mg", "dose_value": "50", "dose_unit": "mg", "status": "active"})
        gold = _mention(surface, concept, [first, second], attribute_provenance={"temporality": [first], **({"dose": [second], "dose_value": [second], "dose_unit": [second], "status": [second]} if surface == "sertralina" else {})}, relation_provenance={"HAS_DOSE": [second]} if surface == "sertralina" else {}, **attrs)
        signals = [] if surface != "sertralina" else [_signal("dose", "50 mg", "medication", "current", "RESOLVED", [second])]
        cases.append(_case(f"D4-{offset:03d}", "CURRENT_HISTORICAL_STATE", [(first, "patient", lead), (second, "patient", answer)], [gold], {"m1": {"attributes": signals, "transitions": []}}))

    transition_rows = [
        ("metformina", "medication.metformin", "dose", "900 mg", "650 mg", "t1", "t2", "A metformina era 900 mg no plano antigo.", "Na revisão, passou para 650 mg."),
        ("atenolol", "medication.atenolol", "frequency", "três vezes ao dia", "duas vezes ao dia", "t1", "t3", "O atenolol era tomado três vezes ao dia.", "A orientação nova deixou duas vezes ao dia."),
        ("losartana", "medication.losartan", "dose", "80 mg", "40 mg", "t1", "t2", "A losartana vinha em 80 mg.", "Depois da consulta, ficou em 40 mg."),
        ("levotiroxina", "medication.levothyroxine", "frequency", "ao acordar", "à noite", "t1", "t3", "Levotiroxina era tomada ao acordar.", "Na prescrição atual, ficou à noite."),
        ("prednisona", "medication.prednisone", "dose", "30 mg", "15 mg", "t1", "t2", "A prednisona começou em 30 mg.", "O esquema de hoje indica 15 mg."),
        ("sertralina", "medication.sertraline", "dose", "75 mg", "100 mg", "t1", "t3", "Sertralina estava ajustada em 75 mg.", "A nova orientação passou para 100 mg."),
    ]
    for offset, (surface, concept, attr, old, new, first, second, lead, answer) in enumerate(transition_rows, 19):
        value = new if attr == "dose" else new
        attrs = {attr: value, "status": "active"}
        if attr == "dose":
            attrs.update({"dose_value": new.split()[0], "dose_unit": "mg"})
        gold = _mention(surface, concept, [first, second], relations=[{"relation_type": "CHANGED_FROM", "target": attr, "value": old}], attribute_provenance={attr: [second], "status": [second], **({"dose_value": [second], "dose_unit": [second]} if attr == "dose" else {})}, relation_provenance={"CHANGED_FROM": [second]}, **attrs)
        cases.append(_case(f"D4-{offset:03d}", "TRANSITION_CONTRACT", [(first, "patient", lead), (second, "patient", answer)], [gold], {"m1": {"attributes": [_signal(attr, value, "medication", "current", "RESOLVED", [second])], "transitions": [_transition(attr, old, new, "medication", "current", "RESOLVED", [second])]}}))

    provenance_rows = [
        ("dor", "symptom.pain", "right", "p1", "p2", "A dor e o formigamento apareceram juntos.", "A dor é do lado direito; o formigamento fica sem lado definido."),
        ("formigamento", "symptom.tingling", "left", "p1", "p3", "O formigamento veio depois da caminhada.", "Ele ficou somente no lado esquerdo."),
        ("metformina", "medication.metformin", "500 mg", "p1", "p2", "Metformina e losartana estão na mesma sacola.", "A etiqueta da metformina marca 500 mg."),
        ("losartana", "medication.losartan", "25 mg", "p1", "p3", "Losartana é o segundo item da conciliação.", "A caixa correspondente informa 25 mg."),
        ("tosse", "symptom.cough", "left", "p1", "p2", "A mãe descreveu tosse e o paciente descreveu dor.", "A dor é à esquerda; a tosse não recebeu lateralidade."),
        ("atenolol", "medication.atenolol", "uma vez ao dia", "p1", "p3", "A lista reúne atenolol e dipirona.", "Para o atenolol, ficou uma vez ao dia."),
    ]
    for offset, (surface, concept, value, first, second, lead, answer) in enumerate(provenance_rows, 25):
        is_attr = "frequency" if "vez" in value else "laterality" if value in {"right", "left"} else "dose"
        attrs: dict[str, Any] = {is_attr: value}
        if is_attr == "dose":
            attrs.update({"dose_value": value.split()[0], "dose_unit": "mg", "status": "active"})
        elif is_attr == "frequency":
            attrs["status"] = "active"
        gold = _mention(surface, concept, [first, second], attribute_provenance={is_attr: [second], **({"dose_value": [second], "dose_unit": [second], "status": [first]} if is_attr == "dose" else {})}, relation_provenance={("HAS_DOSE" if is_attr == "dose" else "HAS_FREQUENCY" if is_attr == "frequency" else "HAS_LATERALITY"): [second]}, **attrs)
        owner_type = "symptom" if is_attr == "laterality" else "medication"
        cases.append(_case(f"D4-{offset:03d}", "CROSS_SEGMENT_PROVENANCE", [(first, "patient", lead), (second, "patient", answer)], [gold], {"m1": {"attributes": [_signal(is_attr, value, owner_type, "current", "RESOLVED", [second])], "transitions": []}}))

    ambiguity_rows = [
        ("medicação", "medication.unknown", "a quantidade ficou diferente", "u1", "u2", "A paciente citou uma medicação sem nome.", "Depois disse apenas que a quantidade ficou diferente.", "UNRESOLVED_OWNER"),
        ("comprimido", "medication.unknown", "o horário mudou", "u1", "u3", "Há dois comprimidos sem identificação na receita.", "O horário mudou, mas não se sabe qual deles.", "AMBIGUOUS"),
        ("tratamento", "treatment.unknown", "a dose foi revista", "u1", "u2", "O tratamento foi mencionado sem entidade específica.", "A dose foi revista sem valor ou dono explícito.", "UNRESOLVED_OWNER"),
        ("sintoma", "symptom.unknown", "fica deste lado", "u1", "u3", "Dois sintomas foram citados na mesma frase.", "A pessoa respondeu que fica deste lado, sem indicar qual.", "AMBIGUOUS"),
        ("remédio", "medication.unknown", "ficou igual", "u1", "u2", "O paciente mencionou mais de um remédio.", "Disse apenas que ficou igual.", "AMBIGUOUS"),
        ("condição", "condition.unknown", "aconteceu antes", "u1", "u3", "A condição não foi identificada com clareza.", "A resposta disse apenas que aconteceu antes.", "UNRESOLVED_STATE"),
    ]
    for offset, (surface, concept, cue, first, second, lead, answer, status) in enumerate(ambiguity_rows, 31):
        gold = _mention(surface, concept, [first, second], temporality="current")
        cases.append(_case(f"D4-{offset:03d}", "AMBIGUITY_UNRESOLVED", [(first, "patient", lead), (second, "patient", answer)], [gold], {"m1": {"attributes": [], "transitions": [{"attribute_type": "unknown", "previous_value": None, "current_value": None, "owner_type": None, "state": "unresolved", "status": status, "source_segment_ids": [second]}]}}))

    return cases


CASES = _build_cases()


def _validate(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if len(records) != 36:
        errors.append(f"expected 36 cases, found {len(records)}")
    ids = [item["case_id"] for item in records]
    if len(ids) != len(set(ids)):
        errors.append("duplicate case ids")
    families: dict[str, int] = {}
    for record in records:
        families[record["scenario_family"]] = families.get(record["scenario_family"], 0) + 1
        segment_ids = {segment["segment_id"] for segment in record["segments"]}
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
    expected = {"OWNER_SENSITIVE_DOSE", "OWNER_SENSITIVE_FREQUENCY", "CURRENT_HISTORICAL_STATE", "TRANSITION_CONTRACT", "CROSS_SEGMENT_PROVENANCE", "AMBIGUITY_UNRESOLVED"}
    if set(families) != expected or set(families.values()) != {6}:
        errors.append(f"family distribution mismatch: {families}")
    return errors


def _candidate_texts() -> list[Path]:
    paths = list((ROOT / "data").glob("*.jsonl")) + list((ROOT / "data").glob("*.json"))
    paths += list((ROOT / "results").glob("*.json"))
    paths += [ROOT.parent.parent / "tests/benchmark/test_relation_input_signals.py", ROOT.parent.parent / "tests/benchmark/test_relation_compiler.py"]
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
        "comparison_scope": "V3-V7, D1-D3, consumed holdouts, C2 tests, and synthetic compiler tests",
    }


def main() -> None:
    errors = _validate(CASES)
    if errors:
        raise RuntimeError("D4 validation failed: " + "; ".join(errors))
    disjointness = _disjointness(CASES)
    if disjointness["status"] != "PASS":
        raise RuntimeError(f"D4 disjointness failed: {disjointness['exact_normalized_text_collisions']}")
    DATA.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in CASES), encoding="utf-8")
    DISJOINTNESS.write_text(json.dumps(disjointness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "status": "D4_FROZEN",
        "benchmark": "D4 Unseen Relation Input Generalization",
        "official_corpus": str(OUTPUT),
        "official_corpus_checksum": _sha256(OUTPUT),
        "policy_version": POLICY_VERSION,
        "policy_checksum": _sha256(POLICY),
        "compiler_checksum": _sha256(COMPILER),
        "c2_schema_checksum": _sha256(C2_SCHEMA),
        "resolver_config_checksum": hashlib.sha256((str(ROOT / "relation_input_signals.py") + _sha256(ROOT / "relation_input_signals.py")).encode()).hexdigest(),
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
        "d1": "CONSUMED_IMMUTABLE",
        "d2": "CONSUMED_IMMUTABLE",
        "d3": "CONSUMED_IMMUTABLE",
        "v7": "CONSUMED_IMMUTABLE",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
