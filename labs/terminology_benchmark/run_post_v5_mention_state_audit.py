"""Audit residual mention-state and cross-mention isolation failures after V5."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus, mention_span
from .context_safety import NieDEPtBrSafetyRules
from .cross_segment_context import CrossSegmentContextAdapter
from .context_harness import _actual_relations, _expected_relations


ROOT = Path(__file__).parent
DOCS = ROOT.parent.parent / "docs" / "clinical-conversational-semantics"
FINAL_RESULT = ROOT / "results" / "context-validation-v6-repair-v5-final-2026-08-15.json"
ADJUDICATION = ROOT / "results" / "v6-residual-type-c-adjudication-2026-08-15.json"
POLICY = "clinical-semantic-policy-v1.1"
FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "status", "dose", "frequency", "relations",
)
ATTRIBUTE_FIELDS = FIELDS[:-1]
SCOPE_FIELDS = ("negated", "certainty", "temporality", "experiencer", "laterality")
STATUS_POLICY = {
    "symptom": ("present", "historical", "resolved", None),
    "condition": ("present", "historical", None),
    "medication": ("active", "discontinued", None),
    "procedure": ("historical", "planned", None),
    "event": ("historical", None),
    "device": ("active", None),
    "person": (None,),
    "time": (None,),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _entity_type(concept_id: str) -> str:
    return concept_id.split(".", 1)[0] if concept_id else "unknown"


def _type_b_fields() -> set[tuple[str, str, int, str]]:
    artifact = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    return {
        (record["case_id"], record["surface"], int(record.get("occurrence", 0)), item["field"])
        for record in artifact["records"]
        for item in record["differing_fields"]
        if item.get("error_type") == "B"
    }


def _field_leak_reason(
    *,
    field: str,
    expected: Any,
    actual: Any,
    gold: Any,
    siblings: tuple[Any, ...],
    result: Any,
) -> str | None:
    if expected == actual:
        return None
    sibling_values = {
        getattr(sibling, field)
        for sibling in siblings
        if getattr(sibling, field) != expected
    }
    if actual in sibling_values and actual != expected:
        return "sibling_expected_value"
    expected_sources = set(gold.attribute_provenance.get(field, ()))
    actual_sources = set(result.provenance.get("segment_provenance", {}).get(field, ()))
    if expected_sources and actual_sources and not actual_sources.issubset(expected_sources):
        return "source_segment_provenance_mismatch"
    return None


async def audit(*, corpus_path: Path, output_dir: Path) -> dict[str, Any]:
    final = json.loads(FINAL_RESULT.read_text(encoding="utf-8"))
    corpus_checksum = _sha256(corpus_path)
    if corpus_checksum != final["official_corpus_sha256"]:
        raise RuntimeError("audit input is not the frozen V6 corpus")
    cases = load_corpus(corpus_path)
    holdout_ids = {"sim-v6-0056", "sim-v6-0057", "sim-v6-0058"}
    if holdout_ids.intersection(case.case_id for case in cases):
        raise RuntimeError("holdouts must not participate in the audit")
    type_b = _type_b_fields()
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)

    failures: list[dict[str, Any]] = []
    status_matrix: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "allowed_status": None,
        "mentions": 0,
        "expected_values": Counter(),
        "actual_values": Counter(),
        "status_mismatches": 0,
        "false_positive": 0,
        "false_negative": 0,
        "wrong_value": 0,
    })
    leakage_items: list[dict[str, Any]] = []
    class_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    mention_total = mention_exact = 0
    relation_total = relation_exact = 0
    cross_segment_total = cross_segment_exact = 0
    per_field_total: Counter[str] = Counter()
    per_field_matches: Counter[str] = Counter()

    for case in cases:
        multi_mention = len(case.gold) > 1
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            result = await adapter.analyze(ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
                semantic_policy=POLICY,
            ))
            entity_type = _entity_type(gold.concept_id)
            matrix = status_matrix[entity_type]
            matrix["allowed_status"] = list(STATUS_POLICY.get(entity_type, (None,)))
            matrix["mentions"] += 1
            matrix["expected_values"][str(gold.status)] += 1
            matrix["actual_values"][str(result.status)] += 1
            ignored = {
                field
                for field in ATTRIBUTE_FIELDS
                if (case.case_id, gold.surface, gold.occurrence, field) in type_b
            }
            mismatches: list[dict[str, Any]] = []
            for field in ATTRIBUTE_FIELDS:
                if field in ignored:
                    continue
                expected = getattr(gold, field)
                actual = getattr(result, field)
                per_field_total[field] += 1
                per_field_matches[field] += int(expected == actual)
                if expected != actual:
                    mismatches.append({"field": field, "expected": expected, "actual": actual})
                    if field == "status":
                        matrix["status_mismatches"] += 1
                        if expected is None and actual is not None:
                            matrix["false_positive"] += 1
                            status_counts["false_positive"] += 1
                        elif expected is not None and actual is None:
                            matrix["false_negative"] += 1
                            status_counts["false_negative"] += 1
                        else:
                            matrix["wrong_value"] += 1
                            status_counts["wrong_value"] += 1

            # Reuse the frozen V6 harness relation semantics, including
            # synthesized HAS_* and DISCONTINUED_AT relations.
            expected_relations = _expected_relations(gold)
            actual_relations = _actual_relations(result)
            if expected_relations:
                relation_total += 1
                relation_exact += int(expected_relations == actual_relations)

            if gold.segment_ids:
                cross_segment_total += 1
                cross_segment_exact += int(not mismatches)

            if mismatches:
                class_name = {
                    ("status",): "only_status",
                    ("temporality",): "only_temporality",
                    ("negated",): "only_negation",
                    ("laterality",): "only_laterality",
                }.get(tuple(item["field"] for item in mismatches), "multiple_fields")
                class_counts[class_name] += 1
                failures.append({
                    "case_id": case.case_id,
                    "surface": gold.surface,
                    "occurrence": gold.occurrence,
                    "text": case.text,
                    "concept_id": gold.concept_id,
                    "entity_type": entity_type,
                    "segment_ids": list(gold.segment_ids),
                    "mismatches": mismatches,
                    "ignored_type_b_fields": sorted(ignored),
                })

            if multi_mention:
                siblings = tuple(item for item in case.gold if item is not gold)
                for field in ATTRIBUTE_FIELDS:
                    if field in ignored:
                        continue
                    reason = _field_leak_reason(
                        field=field,
                        expected=getattr(gold, field),
                        actual=getattr(result, field),
                        gold=gold,
                        siblings=siblings,
                        result=result,
                    )
                    if reason:
                        leakage_items.append({
                            "case_id": case.case_id,
                            "surface": gold.surface,
                            "field": field,
                            "reason": reason,
                            "expected": getattr(gold, field),
                            "actual": getattr(result, field),
                            "segment_ids": list(gold.segment_ids),
                        })

            mention_total += 1
            mention_exact += int(not mismatches)

    for matrix in status_matrix.values():
        matrix["expected_values"] = dict(matrix["expected_values"])
        matrix["actual_values"] = dict(matrix["actual_values"])

    leakage_counts: Counter[str] = Counter()
    leakage_mentions: defaultdict[str, set[str]] = defaultdict(set)
    for item in leakage_items:
        leakage_counts[item["field"]] += 1
        leakage_mentions[item["field"]].add(item["case_id"] + ":" + item["surface"])
    leakage = {
        "definition": "Mismatch where actual equals a sibling gold value or actual provenance comes from a segment outside the target gold provenance.",
        "cross_mention_attribute_leak": len(leakage_items),
        "cross_mention_status_leak": leakage_counts["status"],
        "cross_mention_negation_leak": leakage_counts["negated"],
        "cross_mention_temporality_leak": leakage_counts["temporality"],
        "cross_mention_laterality_leak": leakage_counts["laterality"],
        "affected_mentions_by_field": {field: len(values) for field, values in leakage_mentions.items()},
        "items": leakage_items,
        "relations_frozen": True,
        "provenance_frozen": True,
        "cross_segment_architecture_frozen": True,
    }

    audit_result = {
        "source_final_result": str(FINAL_RESULT),
        "official_corpus_sha256": corpus_checksum,
        "policy": POLICY,
        "type_b_fields_ignored": len(type_b),
        "mentions_total": mention_total,
        "mentions_exact": mention_exact,
        "mentions_failed": mention_total - mention_exact,
        "failure_reason_counts": dict(class_counts),
        "mentions_failed_only_status": class_counts["only_status"],
        "mentions_failed_only_temporality": class_counts["only_temporality"],
        "mentions_failed_only_negation": class_counts["only_negation"],
        "mentions_failed_only_laterality": class_counts["only_laterality"],
        "mentions_failed_multiple_fields": class_counts["multiple_fields"],
        "status_false_positive": status_counts["false_positive"],
        "status_false_negative": status_counts["false_negative"],
        "status_wrong_value": status_counts["wrong_value"],
        "relation_total": relation_total,
        "relation_exact": relation_exact,
        "cross_segment_total": cross_segment_total,
        "cross_segment_exact": cross_segment_exact,
        "field_accuracy": {
            field: per_field_matches[field] / per_field_total[field]
            for field in per_field_total
        },
        "failures": failures,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "POST_V5_STATUS_MATRIX.json").write_text(
        json.dumps({
            "policy": POLICY,
            "official_corpus_sha256": corpus_checksum,
            "entity_types": status_matrix,
            "status_false_positive": status_counts["false_positive"],
            "status_false_negative": status_counts["false_negative"],
            "status_wrong_value": status_counts["wrong_value"],
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "POST_V5_CROSS_MENTION_LEAKAGE.json").write_text(
        json.dumps(leakage, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (ROOT / "results" / "post-v5-mention-state-audit-2026-08-15.json").write_text(
        json.dumps(audit_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md = _render_markdown(audit_result, leakage, status_matrix)
    (output_dir / "POST_V5_MENTION_STATE_AUDIT.md").write_text(md, encoding="utf-8")
    return audit_result


def _render_markdown(audit: dict[str, Any], leakage: dict[str, Any], matrix: dict[str, Any]) -> str:
    lines = [
        "# Post-V5 Mention State & Isolation Audit",
        "",
        "Status: **DIAGNOSTIC ONLY — no repair authorized**  ",
        "Data: 2026-08-15  ",
        f"Policy: `{audit['policy']}`  ",
        f"V6 checksum: `{audit['official_corpus_sha256']}`",
        "",
        "## Escopo e invariantes",
        "",
        "A auditoria reconstrói o caminho policy-aligned do Repair V5 por menção.",
        "Os 10 campos Type B são ignorados somente na comparação do campo", 
        "adjudicado; casos inteiros não são removidos. Resolver, corpus, policy,", 
        "gold, relações, provenance e arquitetura cross-segment não foram alterados.",
        "",
        "## Decomposição de mention_exact_match",
        "",
        f"- mentions_total: **{audit['mentions_total']}**",
        f"- mentions_exact: **{audit['mentions_exact']}**",
        f"- mentions_failed: **{audit['mentions_failed']}**",
        f"- mentions_failed_only_status: **{audit['mentions_failed_only_status']}**",
        f"- mentions_failed_only_temporality: **{audit['mentions_failed_only_temporality']}**",
        f"- mentions_failed_only_negation: **{audit['mentions_failed_only_negation']}**",
        f"- mentions_failed_only_laterality: **{audit['mentions_failed_only_laterality']}**",
        f"- mentions_failed_multiple_fields: **{audit['mentions_failed_multiple_fields']}**",
        "",
        "| Failure reason | Count |",
        "|---|---:|",
    ]
    for key in ("only_status", "only_temporality", "only_negation", "only_laterality", "multiple_fields"):
        lines.append(f"| {key} | {audit['failure_reason_counts'].get(key, 0)} |")
    lines += [
        "",
        "## Status",
        "",
        f"- status_false_positive: **{audit['status_false_positive']}**",
        f"- status_false_negative: **{audit['status_false_negative']}**",
        f"- status_wrong_value: **{audit['status_wrong_value']}**",
        "",
        "| Entity type | Mentions | Expected values | Actual values | Status mismatches |",
        "|---|---:|---|---|---:|",
    ]
    for entity, item in sorted(matrix.items()):
        lines.append(
            f"| {entity} | {item['mentions']} | {item['expected_values']} | "
            f"{item['actual_values']} | {item['status_mismatches']} |"
        )
    lines += [
        "",
        "## Cross-mention leakage",
        "",
        f"- cross_mention_attribute_leak: **{leakage['cross_mention_attribute_leak']}**",
        f"- cross_mention_status_leak: **{leakage['cross_mention_status_leak']}**",
        f"- cross_mention_negation_leak: **{leakage['cross_mention_negation_leak']}**",
        f"- cross_mention_temporality_leak: **{leakage['cross_mention_temporality_leak']}**",
        f"- cross_mention_laterality_leak: **{leakage['cross_mention_laterality_leak']}**",
        "",
        "A definição operacional está no JSON de leakage. Ela é conservadora:",
        "marca apenas valor de sibling gold ou provenance de segmento fora do",
        "owner esperado.",
        "",
        "## Métricas de controle",
        "",
        f"- relation_exact: **{audit['relation_exact']}/{audit['relation_total']}**",
        f"- cross_segment_exact: **{audit['cross_segment_exact']}/{audit['cross_segment_total']}**",
        "- relations: **FROZEN**",
        "- provenance: **FROZEN**",
        "- cross-segment architecture: **FROZEN**",
        "",
        "## Decisão",
        "",
        "Este é um relatório diagnóstico. Não iniciar Repair V6, não alterar gold",
        "ou policy e não executar holdouts, V7, Shadow Integration ou Production.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--output-dir", type=Path, default=DOCS)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(audit(corpus_path=args.corpus, output_dir=args.output_dir)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
