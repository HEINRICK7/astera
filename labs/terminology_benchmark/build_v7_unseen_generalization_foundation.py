"""Build the review-only V7 unseen generalization foundation.

The builder creates dialogue candidates and a human queue. It never creates
GoldMention data, never approves a candidate, and never mutates V3-V6.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DRAFT = DATA / "v7_unseen_generalization_draft.jsonl"
QUEUE = RESULTS / "v7-human-review-queue-2026-08-15.json"
MANIFEST = RESULTS / "v7-corpus-manifest-2026-08-15.json"
DISJOINTNESS = RESULTS / "v7-disjointness-report-2026-08-15.json"
DISJOINTNESS_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_DISJOINTNESS_REPORT.md"


VARIANTS = (
    ("losartana", "metformina", "dor", "mão esquerda", "250 mg", "500 mg", "depois do jantar", "ontem", "minha mãe"),
    ("enalapril", "sertralina", "tontura", "perna direita", "5 mg", "10 mg", "pela manhã", "na semana passada", "meu pai"),
    ("metformina", "atenolol", "náusea", "abdome", "500 mg", "850 mg", "no almoço", "há dois dias", "minha irmã"),
    ("sertralina", "amlodipino", "zumbido", "ouvido esquerdo", "25 mg", "50 mg", "à noite", "no mês passado", "meu irmão"),
    ("atenolol", "levotiroxina", "fraqueza", "braço direito", "25 mg", "50 mg", "antes do café", "há três dias", "minha avó"),
    ("ibuprofeno", "dipirona", "queimação", "pé esquerdo", "200 mg", "400 mg", "se necessário", "desde ontem", "meu avô"),
    ("prednisona", "losartana", "inchaço", "tornozelo direito", "20 mg", "10 mg", "ao acordar", "há uma semana", "minha filha"),
    ("amlodipino", "enalapril", "palpitação", "peito", "5 mg", "20 mg", "duas vezes ao dia", "no mês retrasado", "meu filho"),
    ("levotiroxina", "metformina", "coceira", "braço esquerdo", "75 mcg", "88 mcg", "em jejum", "na consulta anterior", "minha tia"),
    ("dipirona", "sertralina", "cólica", "flanco direito", "500 mg", "1 g", "a cada oito horas", "há quatro dias", "meu tio"),
    ("losartana", "amlodipino", "formigamento", "rosto direito", "25 mg", "10 mg", "de manhã", "no inverno passado", "minha prima"),
    ("enalapril", "prednisona", "tosse", "garganta", "10 mg", "5 mg", "ao deitar", "há quinze dias", "meu primo"),
    ("metformina", "ibuprofeno", "dor", "joelho esquerdo", "500 mg", "600 mg", "após o almoço", "no feriado passado", "minha madrinha"),
    ("sertralina", "dipirona", "vertigem", "lado direito", "50 mg", "100 mg", "à tarde", "no começo do mês", "meu padrinho"),
    ("atenolol", "losartana", "ardor", "pé direito", "25 mg", "50 mg", "ao meio-dia", "há cinco noites", "minha cunhada"),
    ("ibuprofeno", "levotiroxina", "rigidez", "ombro esquerdo", "200 mg", "300 mg", "com alimento", "na última consulta", "meu cunhado"),
    ("prednisona", "sertralina", "falta de ar", "lado esquerdo do peito", "10 mg", "20 mg", "à noite", "há um mês", "minha sogra"),
    ("amlodipino", "metformina", "sensibilidade", "panturrilha direita", "5 mg", "850 mg", "no café da manhã", "no trimestre passado", "meu sogro"),
    ("levotiroxina", "atenolol", "peso", "perna esquerda", "50 mcg", "75 mcg", "antes de dormir", "há seis dias", "minha neta"),
    ("dipirona", "enalapril", "dormência", "mão direita", "500 mg", "10 mg", "quando necessário", "na primavera passada", "meu neto"),
)


def _segments(case_id: str, turns: list[tuple[str, str]]) -> tuple[dict[str, str], ...]:
    return tuple(
        {"segment_id": f"{case_id}:segment-{index:02d}", "speaker": speaker, "text": text}
        for index, (speaker, text) in enumerate(turns, start=1)
    )


def _record(case_id: str, family: str, turns: list[tuple[str, str]], surfaces: list[str], review_dimensions: list[str]) -> dict[str, Any]:
    text = "\n".join(f"{'Médico' if speaker == 'clinician' else 'Paciente'}: {content}" for speaker, content in turns)
    segments = _segments(case_id, turns)
    candidates = []
    for surface in dict.fromkeys(surfaces):
        if surface.casefold() in text.casefold():
            candidates.append({
                "surface": surface,
                "segment_ids": [segment["segment_id"] for segment in segments if surface.casefold() in segment["text"].casefold()],
                "semantic_fields": [],
                "gold_status": "UNSET",
            })
    return {
        "case_id": case_id,
        "version": "v7-draft-0.1",
        "language": "pt-BR",
        "text": text,
        "segments": segments,
        "scenario_family": family,
        "turn_count": len(turns),
        "mention_candidates": candidates,
        "gold": None,
        "review_status": "PENDING_HUMAN",
        "approval_status": "NOT_APPROVED",
        "generator": "deterministic-v7-dialogue-scaffold",
        "gold_generation": "forbidden",
        "review_dimensions": review_dimensions,
    }


def _build_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    families = (
        "MEDICATION_RECONCILIATION",
        "DOSE_TRANSITION",
        "FREQUENCY_STATUS_TRANSITION",
        "MULTIPLE_SYMPTOMS",
        "FAMILY_PATIENT_EXPERIENCER",
        "NEGATION_REVERSAL",
        "DISTRIBUTED_TEMPORALITY",
        "TOPIC_SWITCH",
        "ELLIPTICAL_ANSWER",
        "CLINICIAN_CORRECTION",
        "PATIENT_SELF_CORRECTION",
        "ANAPHORA_SPEAKER_TRANSITION",
    )
    for index, values in enumerate(VARIANTS):
        med_a, med_b, symptom, location, old_dose, new_dose, frequency, temporal, relative = values
        scenarios = (
            [
                ("clinician", f"Vamos revisar seus remédios. Você ainda usa {med_a}?"),
                ("patient", f"Uso {med_a} {old_dose} {frequency}, mas às vezes esqueço."),
                ("clinician", f"E o {med_b}, entrou depois da última consulta?"),
                ("patient", f"Sim, comecei o {med_b}; a receita dizia {new_dose} e continuo assim."),
                ("clinician", f"Então mantenho os dois no esquema atual, correto?"),
            ],
            [
                ("clinician", f"Como ficou a dose do {med_a} depois da mudança?"),
                ("patient", f"Antes era {old_dose} {frequency}."),
                ("clinician", "O que aconteceu na última orientação?"),
                ("patient", f"Eu corrigi: agora uso {new_dose} {frequency} e o ajuste ocorreu {temporal}."),
                ("clinician", "A dose atual é a segunda, não a primeira?"),
                ("patient", "Isso, a segunda é a atual."),
            ],
            [
                ("clinician", f"Com que frequência você toma {med_b}?"),
                ("patient", f"De início era {frequency}, mas mudei o horário."),
                ("clinician", "Você está falando do horário anterior ou do atual?"),
                ("patient", f"Do atual: {frequency}; a mudança foi registrada {temporal}."),
                ("clinician", f"E o {med_a} continua separado dessa rotina?"),
            ],
            [
                ("clinician", f"Além de {symptom}, há outra queixa?"),
                ("patient", f"A {symptom} fica em {location}; também tenho cansaço."),
                ("clinician", "O cansaço começou junto ou depois?"),
                ("patient", f"Depois. A {symptom} é a que mais incomoda agora, mas a outra melhorou {temporal}."),
                ("clinician", "Vou registrar as duas sem misturar os lados."),
            ],
            [
                ("clinician", f"Há {symptom} na família?"),
                ("patient", f"Sim, {relative} teve isso, mas eu não tenho essa queixa."),
                ("clinician", "Quem está com o diagnóstico, então?"),
                ("patient", f"A pessoa da família; eu vim por causa de {location}."),
                ("clinician", "Vou separar o experiencer familiar do paciente."),
            ],
            [
                ("clinician", f"Você sente {symptom}?"),
                ("patient", f"No começo eu disse que sim, mas corrijo: não sinto {symptom}."),
                ("clinician", "E a queixa que permanece?"),
                ("patient", f"Só um desconforto em {location}, sem {symptom}."),
                ("clinician", f"Então a negação vale para {symptom}, não para o desconforto."),
            ],
            [
                ("clinician", f"Quando começou a história de {symptom}?"),
                ("patient", f"A primeira ocorrência foi {temporal}, mas hoje a situação é outra."),
                ("clinician", "O que está presente agora?"),
                ("patient", f"Agora noto a queixa em {location}; o episódio antigo já passou."),
                ("clinician", "Vou manter o tempo do evento separado do estado atual."),
            ],
            [
                ("clinician", f"Vamos falar de {med_a}."),
                ("patient", f"Antes disso, queria comentar {symptom} em {location}."),
                ("clinician", f"Certo; depois voltamos ao {med_a}. O que mudou?"),
                ("patient", f"O {med_a} ficou em {new_dose}; sobre {symptom}, melhorou {temporal}."),
                ("clinician", "São tópicos diferentes e vou mantê-los separados."),
            ],
            [
                ("clinician", f"Qual a dose do {med_a}?"),
                ("patient", f"{new_dose}."),
                ("clinician", f"E a frequência do {med_a}?"),
                ("patient", f"{frequency}."),
                ("clinician", "Essas respostas se referem à mesma medicação?"),
                ("patient", "Sim, à mesma."),
            ],
            [
                ("clinician", f"Você relatou {symptom} ontem, correto?"),
                ("patient", f"Correção: eu quis dizer {location}, não {symptom}."),
                ("clinician", "Entendi; a primeira anotação era uma hipótese?"),
                ("patient", "Era uma confusão na fala, a queixa correta é a segunda."),
                ("clinician", f"Vou manter a correção e não duplicar {symptom}."),
            ],
            [
                ("clinician", f"Você usa {med_a} {old_dose}?"),
                ("patient", f"Usava; pensando melhor, era {new_dose}."),
                ("clinician", "Qual informação vale para o estado atual?"),
                ("patient", f"A dose de {new_dose}, desde {temporal}; a anterior está superada."),
                ("clinician", "Vou registrar a autocorreção e a transição."),
            ],
            [
                ("clinician", f"A pessoa anterior mencionou {symptom}. Você confirma?"),
                ("patient", f"Eu confirmo só a parte sobre {location}; a outra fala era de {relative}."),
                ("clinician", "Agora falando de você, qual medicamento usa?"),
                ("patient", f"Eu uso {med_b} {frequency}, e não tenho {symptom}."),
                ("clinician", "A mudança de falante altera o experiencer, não o tópico automaticamente."),
            ],
        )
        for family_index, turns in enumerate(scenarios, start=1):
            case_number = index * len(scenarios) + family_index
            case_id = f"v7-draft-{case_number:04d}"
            family = families[family_index - 1]
            surfaces = [med_a, med_b, symptom, location, relative]
            review_dimensions = [
                "mention boundaries and concept identity",
                "attribute ownership by segment and speaker",
                "relation endpoints and relation provenance",
                "temporality event-vs-state interpretation",
                "negation and correction scope",
            ]
            records.append(_record(case_id, family, turns, surfaces, review_dimensions))
    if len(records) != 240:
        raise RuntimeError(f"expected 240 V7 draft cases, generated {len(records)}")
    return records


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _existing_texts() -> tuple[set[str], list[str]]:
    paths = [
        DATA / "pt_br_clinical_semantics_v3.jsonl",
        DATA / "pt_br_clinical_semantics_v4.jsonl",
        DATA / "pt_br_clinical_semantics_v5.jsonl",
        DATA / "pt_br_clinical_semantics_v6_draft.jsonl",
        DATA / "pt_br_clinical_semantics_v6.jsonl",
        RESULTS / "v6-human-review-micro-expansion-submission-2026-08-15.json",
        DATA / "post_holdout_generalization_holdout_v2.json",
        RESULTS / "v6-human-review-expansion-submission-2026-08-15.json",
        RESULTS / "v6-human-review-submission-2026-08-15.json",
    ]
    texts: set[str] = set()
    used_paths: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        used_paths.append(str(path))
        try:
            payload = json.loads(path.read_text(encoding="utf-8")) if path.suffix == ".json" else None
        except json.JSONDecodeError:
            payload = None
        if payload is not None:
            items = payload if isinstance(payload, list) else [payload]
            for item in items:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    texts.add(item["text"])
        else:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    if isinstance(item.get("text"), str):
                        texts.add(item["text"])
    return texts, used_paths


def main() -> None:
    records = _build_records()
    existing_texts, source_paths = _existing_texts()
    overlaps = [record["case_id"] for record in records if record["text"] in existing_texts]
    if overlaps:
        raise RuntimeError(f"V7 draft text overlap detected: {overlaps[:5]}")
    if any(record["gold"] is not None or record["review_status"] != "PENDING_HUMAN" for record in records):
        raise RuntimeError("V7 draft must remain gold-free and pending human review")

    DRAFT.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    queue = {
        "status": "HUMAN_REVIEW_REQUIRED",
        "corpus": "v7-unseen-generalization",
        "version": "v7-draft-0.1",
        "candidate_count": len(records),
        "approved_count": 0,
        "pending_count": len(records),
        "gold_generation": "FORBIDDEN",
        "official_evaluation": "BLOCKED",
        "items": [
            {
                "review_id": f"v7-review-{index:04d}",
                "candidate_id": record["case_id"],
                "decision": "PENDING_HUMAN",
                "reviewer": None,
                "review_notes": None,
                "gold": None,
                "review_dimensions": record["review_dimensions"],
                "mention_candidates": record["mention_candidates"],
            }
            for index, record in enumerate(records, start=1)
        ],
    }
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    category_counts = Counter(record["scenario_family"] for record in records)
    disjointness = {
        "status": "PASS_DRAFT_ONLY",
        "draft_corpus": str(DRAFT),
        "draft_case_count": len(records),
        "existing_sources_checked": source_paths,
        "existing_text_count": len(existing_texts),
        "text_overlaps": overlaps,
        "case_id_prefix": "v7-draft-",
        "id_overlap_with_previous": False,
        "gold_overlap_check": "NOT_APPLICABLE_DRAFT_GOLD_EMPTY",
        "holdouts_reused": False,
        "category_counts": dict(category_counts),
        "draft_sha256": _sha256(DRAFT),
        "queue_sha256": _sha256(QUEUE),
        "official_v7_run": False,
    }
    DISJOINTNESS.write_text(json.dumps(disjointness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "status": "DRAFT_NOT_FROZEN",
        "corpus": "V7 Unseen Generalization Foundation",
        "version": "v7-draft-0.1",
        "draft_path": str(DRAFT),
        "review_queue_path": str(QUEUE),
        "disjointness_report_path": str(DISJOINTNESS),
        "case_count": len(records),
        "category_counts": dict(category_counts),
        "gold_approved": 0,
        "human_review_complete": False,
        "gold_validation_complete": False,
        "corpus_freeze_complete": False,
        "official_evaluation": "BLOCKED",
        "resolver_changed": False,
        "policy_version": "1.2",
        "holdouts_reused": False,
        "v7_foundation_ready": False,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DISJOINTNESS_MD.write_text(
        "# V7 Disjointness Report\n\n"
        "Status: **PASS — DRAFT ONLY**\n\n"
        f"Generated `{len(records)}` V7 cases with no exact-text overlap against the checked V3–V6 sources and consumed holdout sources.\n\n"
        "- gold approved: `0`\n"
        "- human review: `PENDING`\n"
        "- official V7 execution: `BLOCKED`\n"
        "- old holdouts reused: `false`\n"
        f"- draft SHA-256: `{disjointness['draft_sha256']}`\n\n"
        "The report proves draft disjointness only. It does not approve semantic gold or authorize evaluation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "DRAFT_NOT_FROZEN", "cases": len(records), "draft": str(DRAFT), "queue": str(QUEUE), "manifest": str(MANIFEST), "disjointness": str(DISJOINTNESS)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
