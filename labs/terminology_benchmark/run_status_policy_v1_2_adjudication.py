"""Prepare the human adjudication queue for Clinical Status Policy v1.2."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus


ROOT = Path(__file__).parent
DOCS = ROOT.parent.parent / "docs" / "clinical-conversational-semantics"
AUDIT = ROOT / "results" / "post-v5-mention-state-audit-2026-08-15.json"
POLICY = "clinical-semantic-policy-v1.1 (under review; v1.2 not approved)"

TEMPORAL_PATTERNS = (
    r"\bhá anos?\b", r"\bhá meses?\b", r"\bdesde ontem\b", r"\bontem\b",
    r"\bhoje\b", r"\bdepois do almoço\b", r"\bao acordar\b",
    r"\bsemana passada\b", r"\bmês passado\b", r"\bno passado\b",
    r"\batualmente\b", r"\bna consulta de hoje\b", r"\bretorno desta semana\b",
)
LIFECYCLE_PATTERNS = (
    r"\bpersiste\b", r"\bcontinua(?: com| a)?\b", r"\bpermanece\b",
    r"\bresolveu\b", r"\bresolvido\b", r"\bmelhorou\b", r"\bdesapareceu\b",
    r"\bparou\b", r"\bsuspendeu\b", r"\binterrompeu\b", r"\bretomou\b",
    r"\bvoltou a\b", r"\bmantém\b", r"\bainda usa\b", r"\busa\b",
    r"\btoma\b", r"\btomava\b",
)
NEGATION_PATTERNS = (r"\bnega\b", r"\bnão\b", r"\bnunca\b", r"\bsem\b")
CLASSIFICATIONS = (
    "EXPLICIT_LIFECYCLE_STATUS",
    "IMPLICIT_ASSERTION_ONLY",
    "TEMPORALITY_ONLY",
    "NEGATION_ONLY",
    "MEDICATION_LIFECYCLE",
    "PROCEDURE_LIFECYCLE",
    "EVENT_LIFECYCLE",
    "NO_STATUS_EVIDENCE",
)
CANDIDATE_ENTITY_MATRIX = {
    "symptom": {
        "default_status": None,
        "explicit_lifecycle_values": ["ongoing", "resolved"],
        "temporal_history_representation": "temporality=past; status=null",
    },
    "condition": {
        "default_status": None,
        "explicit_lifecycle_values": ["ongoing", "resolved"],
        "temporal_history_representation": "temporality=past; status=null",
    },
    "person": {
        "default_status": None,
        "explicit_lifecycle_values": [],
        "temporal_history_representation": "experiencer mention does not inherit event status",
    },
    "event": {
        "default_status": None,
        "explicit_lifecycle_values": [],
        "temporal_history_representation": "temporality=past; status=null",
    },
    "procedure": {
        "default_status": None,
        "explicit_lifecycle_values": ["planned"],
        "temporal_history_representation": "temporality=past; status=null",
    },
    "medication": {
        "default_status": "lifecycle_explicit",
        "explicit_lifecycle_values": ["active", "discontinued"],
        "temporal_history_representation": "discontinuation event owns past time",
    },
    "device": {
        "default_status": "lifecycle_explicit",
        "explicit_lifecycle_values": ["active", "discontinued"],
        "temporal_history_representation": "discontinuation event owns past time",
    },
}


def _matches(patterns: tuple[str, ...], text: str) -> list[str]:
    return [pattern for pattern in patterns if re.search(pattern, text, flags=re.I)]


def _entity_type(concept_id: str) -> str:
    return concept_id.split(".", 1)[0] if concept_id else "unknown"


def _status_evidence(
    *,
    entity_type: str,
    text: str,
    surface: str,
    gold: Any,
    expected_status: Any,
    resolved_status: Any,
) -> dict[str, Any]:
    temporal_cues = _matches(TEMPORAL_PATTERNS, text)
    lifecycle_cues = _matches(LIFECYCLE_PATTERNS, text)
    negation_cues = _matches(NEGATION_PATTERNS, text)

    # These are evidence flags, not semantic decisions. A cue in a sibling
    # clause is intentionally retained for human review rather than applied
    # to the target mention automatically.
    target_negated = bool(getattr(gold, "negated", False))
    target_temporality = getattr(gold, "temporality", None)
    explicit_target_lifecycle = (
        any(re.search(pattern, surface, flags=re.I) for pattern in ())
        or (entity_type in {"medication", "device"} and bool(lifecycle_cues))
    )

    if entity_type == "medication" and lifecycle_cues:
        classification = "MEDICATION_LIFECYCLE"
    elif entity_type == "procedure":
        classification = "PROCEDURE_LIFECYCLE"
    elif entity_type == "event":
        classification = "EVENT_LIFECYCLE"
    elif explicit_target_lifecycle:
        classification = "EXPLICIT_LIFECYCLE_STATUS"
    elif target_negated and not target_temporality:
        classification = "NEGATION_ONLY"
    elif resolved_status == "historical" and expected_status is None and entity_type == "person":
        classification = "TEMPORALITY_ONLY"
    elif resolved_status == "historical" and expected_status is None and temporal_cues:
        classification = "TEMPORALITY_ONLY"
    elif getattr(gold, "status", None) is not None:
        classification = "IMPLICIT_ASSERTION_ONLY"
    else:
        classification = "NO_STATUS_EVIDENCE"

    # Candidate matrix only. This value is deliberately not written back to
    # gold, policy, resolver output, or benchmark metrics.
    if entity_type in {"medication", "device"}:
        proposed = "retain_explicit_lifecycle_only"
    elif classification in {"EXPLICIT_LIFECYCLE_STATUS", "MEDICATION_LIFECYCLE"}:
        proposed = "human_decision_required"
    else:
        proposed = None

    return {
        "classification": classification,
        "temporal_cues": temporal_cues,
        "lifecycle_cues": lifecycle_cues,
        "negation_cues": negation_cues,
        "target_negated": target_negated,
        "target_temporality": target_temporality,
        "explicit_target_lifecycle": explicit_target_lifecycle,
        "proposed_normative_status": proposed,
        "cue_scope_warning": bool(negation_cues or lifecycle_cues or temporal_cues),
    }


def _load_gold_index() -> dict[tuple[str, str, int], Any]:
    index: dict[tuple[str, str, int], Any] = {}
    for case in load_corpus(CONTEXT_VALIDATION_V6_PATH):
        for gold in case.gold:
            index[(case.case_id, gold.surface, gold.occurrence)] = gold
    return index


def build_queue() -> dict[str, Any]:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    gold_index = _load_gold_index()
    records: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    by_entity: defaultdict[str, Counter[str]] = defaultdict(Counter)
    by_transition: Counter[str] = Counter()

    for failure in audit["failures"]:
        status_mismatch = next(
            (item for item in failure["mismatches"] if item["field"] == "status"),
            None,
        )
        if status_mismatch is None:
            continue
        key = (failure["case_id"], failure["surface"], int(failure["occurrence"]))
        gold = gold_index[key]
        evidence = _status_evidence(
            entity_type=failure["entity_type"],
            text=failure["text"],
            surface=failure["surface"],
            gold=gold,
            expected_status=status_mismatch["expected"],
            resolved_status=status_mismatch["actual"],
        )
        status_only = len(failure["mismatches"]) == 1
        record = {
            "case_id": failure["case_id"],
            "entity_type": failure["entity_type"],
            "text": failure["text"],
            "surface": failure["surface"],
            "occurrence": failure["occurrence"],
            "segment_ids": failure["segment_ids"],
            "gold_status": status_mismatch["expected"],
            "resolved_status": status_mismatch["actual"],
            "negation": gold.negated,
            "certainty": gold.certainty,
            "temporality": gold.temporality,
            "experiencer": gold.experiencer,
            "explicit_status_cue": evidence["lifecycle_cues"],
            "temporal_cues": evidence["temporal_cues"],
            "negation_cues": evidence["negation_cues"],
            "status_failure_scope": "only_status" if status_only else "status_plus_other_field",
            "classification": evidence["classification"],
            "proposed_normative_status": evidence["proposed_normative_status"],
            "rationale": (
                "Candidate v1.2 treats status as lifecycle/state only; "
                "human adjudication is required before changing policy."
            ),
            "cue_scope_warning": evidence["cue_scope_warning"],
            "type_b_fields_ignored": failure["ignored_type_b_fields"],
        }
        records.append(record)
        counts[record["classification"]] += 1
        by_entity[record["entity_type"]][record["classification"]] += 1
        by_transition[f"{record['gold_status']} → {record['resolved_status']}"] += 1

    records.sort(key=lambda item: (item["case_id"], item["surface"], item["occurrence"]))
    return {
        "status": "HUMAN_GATE_REQUIRED",
        "policy": POLICY,
        "source_audit": str(AUDIT),
        "frozen_corpus_sha256": audit["official_corpus_sha256"],
        "status_mismatch_findings": len(records),
        "status_only_failures": sum(item["status_failure_scope"] == "only_status" for item in records),
        "status_plus_other_field": sum(item["status_failure_scope"] != "only_status" for item in records),
        "classification_counts": {key: counts[key] for key in CLASSIFICATIONS},
        "by_entity_type": {key: dict(sorted(value.items())) for key, value in sorted(by_entity.items())},
        "status_transitions": dict(sorted(by_transition.items())),
        "records": records,
        "decision_required": [
            "whether positive assertion alone produces status=present",
            "whether historical event/procedure/person cues produce status or only temporality",
            "whether symptom lifecycle values such as ongoing/resolved are approved",
            "whether resolved may coexist with negated=true",
        ],
        "mutations": {
            "resolver_changes": 0,
            "gold_changes": 0,
            "corpus_changes": 0,
            "policy_changes": 0,
            "repair_started": False,
        },
    }


def render_markdown(queue: dict[str, Any]) -> str:
    lines = [
        "# Clinical Status Semantics Adjudication — Policy v1.2",
        "",
        "Status: **HUMAN GATE — POLICY v1.2 NOT APPROVED**  ",
        f"Policy under review: `{queue['policy']}`  ",
        f"Frozen V6 checksum: `{queue['frozen_corpus_sha256']}`",
        "",
        "## Escopo",
        "",
        "Esta fila usa somente divergências de `status` do audit pós-V5. "
        "Não altera resolver, gold, corpus, policy ou métricas. "
        "Os 89 casos `only_status` são falhas de menção exclusivamente por status; "
        "há 90 findings de campo porque um caso também diverge em negação.",
        "",
        "## Contagens",
        "",
        f"- status mismatch findings: **{queue['status_mismatch_findings']}**",
        f"- status-only failures: **{queue['status_only_failures']}**",
        f"- status plus another field: **{queue['status_plus_other_field']}**",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for key, value in queue["classification_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Matriz por entidade",
        "",
        "| Entity type | Classification | Count |",
        "|---|---|---:|",
    ]
    for entity, values in queue["by_entity_type"].items():
        for classification, count in values.items():
            lines.append(f"| {entity} | {classification} | {count} |")
    lines += [
        "",
        "## Transições observadas",
        "",
        "| Gold → resolved | Count |",
        "|---|---:|",
    ]
    for transition, count in queue["status_transitions"].items():
        lines.append(f"| {transition} | {count} |")
    lines += [
        "",
        "## Hipótese normativa candidata (não aplicada)",
        "",
        "- symptom/condition/person/event/procedure: `status=null` por default;",
        "  lifecycle explícito exigiria decisão normativa própria;",
        "- medication/device: preservar somente lifecycle explícito (`active`,",
        "  `discontinued` ou vocabulário aprovado);",
        "- passado de evento não deve transferir automaticamente `historical` para",
        "  a menção nem para o experiencer; pode ser apenas `temporality=past`.",
        "",
        "Essa é uma hipótese para adjudicação, não uma nova versão da policy.",
        "",
        "## Decisões humanas necessárias",
        "",
    ]
    for item in queue["decision_required"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Fila completa",
        "",
        "Os 90 findings, com texto, cues, valores e classificação, estão no JSON",
        "`STATUS_EXPLICIT_CUE_ANALYSIS.json`.",
        "",
        "## Invariantes",
        "",
        "- resolver_changes = 0",
        "- gold_changes = 0",
        "- corpus_changes = 0",
        "- policy_changes = 0",
        "- repair_started = false",
        "- relations, provenance e cross-segment architecture permanecem frozen",
        "- holdouts, V7, Shadow e Production permanecem bloqueados",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    queue = build_queue()
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "STATUS_EXPLICIT_CUE_ANALYSIS.json").write_text(
        json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (DOCS / "STATUS_ENTITY_MATRIX.json").write_text(
        json.dumps({
            "policy": POLICY,
            "status": "candidate_matrix_only",
            "entity_types": queue["by_entity_type"],
            "candidate_allowed_status": CANDIDATE_ENTITY_MATRIX,
            "status_mismatch_findings": queue["status_mismatch_findings"],
            "status_transitions": queue["status_transitions"],
            "frozen_v6_checksum": queue["frozen_corpus_sha256"],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (DOCS / "STATUS_POLICY_V1_2_ADJUDICATION.md").write_text(
        render_markdown(queue), encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in queue.items() if key != "records"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
