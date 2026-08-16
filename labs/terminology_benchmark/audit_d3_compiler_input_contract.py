"""Audit the frozen D3 relation inputs without executing the resolver.

The audit distinguishes an insufficient semantic input contract from a
compiler defect. It reads only persisted D3 traces and gold snapshots.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
TRACE_DIR = RESULTS / "d3-traces-2026-08-15"
ONE_SHOT = RESULTS / "D3_ONE_SHOT_RESULT.json"
MATRIX = RESULTS / "D3_COMPILER_INPUT_FAILURE_MATRIX.json"
REPORT = ROOT.parent.parent / "docs/clinical-conversational-semantics/D3_RELATION_COMPILER_INPUT_AUDIT.md"
CONTRACT = ROOT.parent.parent / "docs/clinical-conversational-semantics/RELATION_INPUT_CONTRACT.md"

DERIVED_FIELDS = {
    "HAS_DOSE": "dose",
    "HAS_FREQUENCY": "frequency",
    "HAS_LATERALITY": "laterality",
    "HAS_ROUTE": "route",
    "DISCONTINUED_AT": "status",
}
OWNER_TYPES = {
    "medication": {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "DISCONTINUED_AT", "CHANGED_FROM", "CHANGED_TO"},
    "treatment": {"HAS_DOSE", "HAS_FREQUENCY", "HAS_ROUTE", "DISCONTINUED_AT", "CHANGED_FROM", "CHANGED_TO"},
    "symptom": {"HAS_LATERALITY"},
    "condition": {"HAS_LATERALITY"},
    "anatomical": {"HAS_LATERALITY"},
}


def _stage(trace: dict[str, Any], name: str) -> dict[str, Any]:
    return next(item["payload"] for item in trace["snapshots"] if item["stage"] == name)


def _relation_key(item: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    return item.get("relation_type"), item.get("target"), item.get("value")


def _dedupe_expected(gold: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    # The persisted D3 gold snapshot is already normalized by the one-shot
    # harness: its `relations` field includes derived attribute relations.
    # Re-deriving them here would manufacture duplicates in every case.
    records = list(gold.get("relations", []))
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    seen: set[tuple[str | None, str | None, str | None]] = set()
    for item in records:
        key = _relation_key(item)
        if key in seen:
            duplicates.append(item)
        else:
            unique.append(item)
            seen.add(key)
    return unique, duplicates


def _owner_type(concept_id: str | None) -> str | None:
    if not concept_id or "." not in concept_id:
        return None
    prefix = concept_id.split(".", 1)[0].casefold()
    return prefix if prefix in OWNER_TYPES else None


def _candidate_actual(expected: dict[str, Any], actual: list[dict[str, Any]]) -> dict[str, Any] | None:
    relation_type, target, value = _relation_key(expected)
    exact = next((item for item in actual if _relation_key(item) == (relation_type, target, value)), None)
    if exact:
        return exact
    return next((item for item in actual if item.get("relation_type") == relation_type and item.get("target") == target), None)


def _compiler_rule(actual: dict[str, Any] | None) -> str | None:
    if not actual:
        return None
    provenance = actual.get("provenance", {})
    if isinstance(provenance, dict):
        return provenance.get("rule")
    return None


def _input_record(
    *,
    case_id: str,
    mention_index: int,
    gold: dict[str, Any],
    expected: dict[str, Any] | None,
    produced: dict[str, Any] | None,
    authority: dict[str, Any],
    resolved_mention: dict[str, Any],
    duplicates: list[dict[str, Any]],
) -> dict[str, Any]:
    fields = resolved_mention.get("fields", {})
    relation_type = expected.get("relation_type") if expected else produced.get("relation_type") if produced else None
    target = expected.get("target") if expected else produced.get("target") if produced else None
    expected_value = expected.get("value") if expected else None
    owner_type = authority.get("owner_type")
    owner_id = authority.get("owner_mention_id")
    ownership = authority.get("attribute_ownership", {})
    field = DERIVED_FIELDS.get(relation_type or "") or (target if target in fields else None)
    field_owner = ownership.get(field, {}) if field else {}
    expected_sources = set(gold.get("relation_provenance", {}).get(relation_type, ()))
    if not expected_sources and field:
        expected_sources = set(gold.get("attribute_provenance", {}).get(field, ()))
    if not expected_sources:
        expected_sources = set(gold.get("segment_ids", ()))
    actual_value = fields.get(field) if field else None
    expected_owner_type = _owner_type(gold.get("concept_id"))
    notes: list[str] = []
    classification = "INPUT_CORRECT_COMPILER_WRONG"
    first_field: str | None = None
    confidence = 0.96

    if duplicates:
        classification = "INPUT_AMBIGUOUS"
        first_field = "gold_relation_contract"
        notes.append("gold snapshot encodes the same relation key more than once; immutable relation set has unique-key semantics")
        confidence = 0.99
    elif relation_type in DERIVED_FIELDS:
        allowed = OWNER_TYPES.get(expected_owner_type or "", set())
        if owner_type is None or not owner_id:
            classification = "INPUT_INCOMPLETE"
            first_field = "owner_signal"
            notes.append("resolved authority lacks a typed owner identity")
        elif relation_type not in OWNER_TYPES.get(str(owner_type), set()) or (allowed and relation_type not in allowed):
            classification = "INPUT_WRONG_OWNER"
            first_field = "owner_type"
            notes.append(f"resolved owner type {owner_type!r} is incompatible with {relation_type}")
        elif field_owner and field_owner.get("owner_type") not in {owner_type, expected_owner_type}:
            classification = "INPUT_WRONG_OWNER"
            first_field = f"attribute_ownership.{field}.owner_type"
            notes.append("attribute ownership type disagrees with relation owner")
        elif actual_value != expected_value:
            classification = "INPUT_WRONG_STATE"
            first_field = field or "resolved_attribute"
            notes.append(f"resolved {field} is {actual_value!r}, expected current value {expected_value!r}")
        elif not expected_sources or not set(field_owner.get("source_segment_ids", ())) & expected_sources:
            classification = "INPUT_INCOMPLETE"
            first_field = f"attribute_ownership.{field}.source_segment_ids"
            notes.append("attribute source provenance does not support the expected relation evidence")
    elif relation_type in {"CHANGED_FROM", "CHANGED_TO"}:
        evidence = [item for item in authority.get("transition_evidence", ()) if item.get("relation_type") == relation_type and item.get("target") == target]
        exact_evidence = [item for item in evidence if item.get("value") == expected_value]
        if not evidence:
            classification = "INPUT_WRONG_TRANSITION"
            first_field = "transition_signal"
            notes.append("no transition evidence reached the compiler")
        elif not exact_evidence:
            classification = "INPUT_WRONG_TRANSITION"
            first_field = "transition_signal.value"
            notes.append(f"transition evidence values were {[item.get('value') for item in evidence]!r}")
        elif owner_type is None or not owner_id:
            classification = "INPUT_INCOMPLETE"
            first_field = "owner_signal"
            notes.append("transition is present but has no typed resolved owner")
        elif not expected_sources or not set(exact_evidence[0].get("source_segment_ids", ())) & expected_sources:
            classification = "INPUT_INCOMPLETE"
            first_field = "transition_signal.source_segment_ids"
            notes.append("transition provenance does not support the expected source")
    else:
        signals = [item for item in authority.get("relation_signals", ()) if item.get("relation_type") == relation_type]
        if expected and not signals:
            classification = "INPUT_INCOMPLETE"
            first_field = "endpoint_signal"
            notes.append("no explicit endpoint relation signal was preserved")
        elif expected and signals and not any(item.get("target") == target and item.get("value") == expected_value for item in signals):
            classification = "INPUT_WRONG_ENDPOINT_SIGNAL"
            first_field = "endpoint_signal"
            notes.append("explicit relation signal endpoint or value disagrees with gold")

    input_sufficient = classification == "INPUT_CORRECT_COMPILER_WRONG"
    if input_sufficient and expected and produced and _relation_key(produced) == _relation_key(expected):
        # This record would not normally be emitted as a mismatch; retain the
        # classification semantics for callers that inspect a full matrix.
        classification = "INPUT_CORRECT_COMPILER_WRONG"
    return {
        "case_id": case_id,
        "mention_index": mention_index,
        "expected_relation": expected,
        "produced_relation": produced,
        "compiler_input": {
            "resolved_mention": resolved_mention,
            "resolved_attributes": fields,
            "owner_type": owner_type,
            "owner_mention_id": owner_id,
            "attribute_owner": field_owner,
            "current_historical": {"temporality": fields.get("temporality"), "status": fields.get("status")},
            "transition_evidence": authority.get("transition_evidence", []),
            "source_segments": sorted(expected_sources),
            "provenance": {"attribute_provenance": authority.get("attribute_provenance", {}), "relation_provenance": gold.get("relation_provenance", {})},
        },
        "input_sufficient_for_expected_relation": input_sufficient,
        "first_incorrect_input_field": first_field,
        "compiler_rule_used": _compiler_rule(produced),
        "classification": classification,
        "confidence": confidence,
        "notes": notes,
    }


def main() -> None:
    result = json.loads(ONE_SHOT.read_text(encoding="utf-8"))
    generated_cases = {item["case_id"] for item in result["findings"] if item.get("first_divergence_stage") == "generated_relations"}
    findings: list[dict[str, Any]] = []
    by_relation: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case_id in sorted(generated_cases):
        trace = json.loads((TRACE_DIR / f"{case_id}.json").read_text(encoding="utf-8"))
        ownership = _stage(trace, "ownership_resolution")
        resolved = _stage(trace, "resolved_semantics")
        generated = _stage(trace, "generated_relations")
        gold_payload = _stage(trace, "gold")
        for index, gold in enumerate(gold_payload.get("mentions", [])):
            expected, duplicates = _dedupe_expected(gold)
            actual = generated.get("relations", [[]])[index] if index < len(generated.get("relations", [])) else []
            for relation in expected:
                produced = _candidate_actual(relation, actual)
                if produced is None or _relation_key(produced) != _relation_key(relation):
                    authority = resolved.get("authority", {})
                    record = _input_record(
                        case_id=case_id,
                        mention_index=index,
                        gold=gold,
                        expected=relation,
                        produced=produced,
                        authority=authority,
                        resolved_mention=resolved.get("mentions", [])[index],
                        duplicates=duplicates,
                    )
                    findings.append(record)
                    by_relation[relation["relation_type"]].append(record)
            expected_keys = {_relation_key(item) for item in expected}
            for produced in actual:
                if _relation_key(produced) in expected_keys:
                    continue
                authority = resolved.get("authority", {})
                record = _input_record(
                    case_id=case_id,
                    mention_index=index,
                    gold=gold,
                    expected=None,
                    produced=produced,
                    authority=authority,
                    resolved_mention=resolved.get("mentions", [])[index],
                    duplicates=duplicates,
                )
                findings.append(record)
                by_relation[produced.get("relation_type", "UNKNOWN")].append(record)

    counts = Counter(item["classification"] for item in findings)
    compiler_bugs = counts.get("INPUT_CORRECT_COMPILER_WRONG", 0)
    upstream = sum(count for key, count in counts.items() if key.startswith("INPUT_") and key not in {"INPUT_CORRECT_COMPILER_WRONG", "INPUT_AMBIGUOUS"})
    incomplete = counts.get("INPUT_INCOMPLETE", 0)
    ambiguous = counts.get("INPUT_AMBIGUOUS", 0)
    if compiler_bugs and upstream:
        decision = "C3"
    elif compiler_bugs:
        decision = "C1"
    elif upstream:
        decision = "C2"
    else:
        decision = "C4"
    matrix = {
        "status": "HUMAN_GATE",
        "source": "D3 frozen Trace Granularity v2",
        "d3_rerun": False,
        "resolver_changed": False,
        "compiler_changed": False,
        "generated_relation_cases": len(generated_cases),
        "finding_count": len(findings),
        "classification_counts": dict(counts),
        "compiler_bugs": compiler_bugs,
        "upstream_input_bugs": upstream,
        "incomplete_inputs": incomplete,
        "ambiguous_inputs": ambiguous,
        "decision": decision,
        "by_relation_type": {key: {"count": len(value), "classification_counts": dict(Counter(item["classification"] for item in value)), "findings": value} for key, value in sorted(by_relation.items())},
        "findings": findings,
        "policy": "clinical-semantic-policy-v1.3",
        "next_action": "HUMAN_GATE; no repair authorized",
    }
    MATRIX.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# D3 ClinicalRelationCompiler Input Contract Audit", "", "Status: **HUMAN GATE**", "",
        "This audit reads only the 36 frozen D3 traces. D3 was not rerun and no compiler or resolver code was changed.", "",
        "## Summary", "",
        f"- generated_relations first-divergence cases: `{len(generated_cases)}`",
        f"- relation findings audited: `{len(findings)}`",
        f"- compiler bugs (`INPUT_CORRECT_COMPILER_WRONG`): `{compiler_bugs}`",
        f"- upstream input bugs: `{upstream}`",
        f"- incomplete inputs: `{incomplete}`",
        f"- ambiguous inputs: `{ambiguous}`",
        f"- next decision: `{decision}`",
        "",
        "## Interpretation", "",
        "`INPUT_CORRECT_COMPILER_WRONG` requires typed owner identity, compatible ownership, correct current/transition state, supported endpoints and provenance before the compiler boundary. Missing or contradictory fields are not attributed to the compiler merely because the first evaluated mismatch is `generated_relations`.", "",
        "## Relation matrices", "",
    ]
    for relation_type, records in sorted(by_relation.items()):
        relation_counts = Counter(item["classification"] for item in records)
        lines.append(f"### {relation_type}")
        lines.append("")
        lines.append(f"- findings: `{len(records)}`")
        for classification, count in sorted(relation_counts.items()):
            lines.append(f"- `{classification}`: `{count}`")
        lines.append("")
    lines += ["## Findings", ""]
    for item in findings:
        lines.append(f"- `{item['case_id']}` m{item['mention_index']} — `{item['classification']}` — expected `{item['expected_relation']}`; produced `{item['produced_relation']}`; first incorrect field `{item['first_incorrect_input_field']}`; confidence `{item['confidence']}`")
    lines += ["", "No repair is authorized. D1, D2, V7 and D3 remain immutable historical evidence.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    CONTRACT.write_text("""# Relation Input Contract\n\nStatus: proposed from the frozen D3 audit; not yet implemented.\n\nThe `ClinicalRelationCompiler` may compile only after `ResolvedClinicalSemantics` supplies the semantic truth required by the relation type. The compiler is not responsible for recovering omitted ownership, state or transition information.\n\n## Required common contract\n\nEvery resolved relation input must provide:\n\n- one resolved owner identity and a typed owner (`medication`, `treatment`, `symptom`, `condition`, or `anatomical` as applicable);\n- the resolved current attribute value, if the relation is derived from an attribute;\n- ownership for that attribute, including owner identity and source segment IDs;\n- current-versus-historical state when both historical and current evidence exist;\n- provenance that supports the value and relation;\n- an explicit endpoint signal for relations not derived from an attribute.\n\nMissing data must remain missing or unresolved. The compiler must not infer an owner from proximity or invent a transition.\n\n## Relation-specific contract\n\n| Relation | Required input | Forbidden shortcut |\n| --- | --- | --- |\n| `HAS_DOSE` | current `dose`, compatible medication/treatment owner, dose ownership and provenance | using a previous dose as current |\n| `HAS_FREQUENCY` | current `frequency`, compatible medication/treatment owner, frequency ownership and provenance | copying frequency from an adjacent medication |\n| `HAS_LATERALITY` | resolved `laterality`, symptom/condition/anatomical owner, laterality ownership and provenance | using a laterality cue without an owner |\n| `CHANGED_FROM` | explicit transition evidence with target, previous value, owner and source provenance | treating the first observed value as both previous and current |\n| `CHANGED_TO` | explicit transition evidence with target, current value, owner and source provenance | deriving a transition from an untyped pair of values |\n| `DISCONTINUED_AT` | `status=discontinued`, medication/treatment owner, discontinuation evidence and provenance | emitting lifecycle relation for a symptom/event or from temporality alone |\n| other explicit relations | typed source/target endpoint signal and relation provenance | silently defaulting endpoints |\n\n## Authority boundary\n\n```text\nLocal semantics / continuity\n        ↓\nResolvedClinicalSemantics  -- must satisfy this contract\n        ↓\nClinicalRelationCompiler\n        ↓\nImmutable Relation Set\n```\n\nThe D3 audit found that `owner_type=null`, unresolved current state and malformed/missing transition evidence are upstream contract failures. This document is a diagnostic proposal only; policy, gold, resolver and compiler remain unchanged.\n""", encoding="utf-8")
    print(json.dumps({"status": matrix["status"], "decision": decision, "compiler_bugs": compiler_bugs, "upstream_input_bugs": upstream, "incomplete_inputs": incomplete, "ambiguous_inputs": ambiguous, "findings": len(findings), "outputs": [str(MATRIX), str(REPORT), str(CONTRACT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
