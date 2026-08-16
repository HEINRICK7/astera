"""Offline D1/D2 relation architecture audit.

Reads only frozen traces and source text.  It never imports or executes the
clinical resolver and writes diagnostic artifacts only.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
DOCS = ROOT.parent.parent / "docs/clinical-conversational-semantics"
TRACE_SETS = {
    "D1": RESULTS / "d1-traces-2026-08-15",
    "D2": RESULTS / "d2-traces-2026-08-15",
}
DERIVED = {
    "HAS_DOSE": "dose",
    "HAS_FREQUENCY": "frequency",
    "HAS_ROUTE": "route",
    "HAS_LATERALITY": "laterality",
    "DISCONTINUED_AT": "status",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _key(item: dict[str, Any]) -> tuple[str, str, str | None]:
    return item.get("relation_type", ""), item.get("target", ""), item.get("value")


def _counter(items: list[dict[str, Any]]) -> Counter[tuple[str, str, str | None]]:
    return Counter(_key(item) for item in items)


def _first_mention(snapshot: dict[str, Any], key: str = "mentions") -> dict[str, Any]:
    items = snapshot.get("payload", {}).get(key, [])
    return items[0] if items else {}


def _classify(expected: list[dict[str, Any]], actual: list[dict[str, Any]], resolved: dict[str, Any], gold: dict[str, Any]) -> tuple[str, str]:
    expected_counts = _counter(expected)
    actual_counts = _counter(actual)
    missing = list((expected_counts - actual_counts).elements())
    extra = list((actual_counts - expected_counts).elements())
    resolved_fields = resolved.get("fields", {})
    gold_fields = gold.get("fields", {})

    if any(count > 1 for count in expected_counts.values()) or any(count > 1 for count in actual_counts.values()):
        if any(count > 1 for count in expected_counts.values()) and all(count <= 1 for count in actual_counts.values()):
            return "RELATION_DUPLICATION", "expected-side duplicate; likely explicit relation plus derived expansion"
        return "RELATION_DUPLICATION", "duplicate semantic relation key in relation set"

    if missing:
        if any(item[0] == "CHANGED_FROM" for item in missing):
            return "TRANSITION_COMPILATION", "transition relation expected but not emitted"
        for relation_type, target, value in missing:
            field = DERIVED.get(relation_type)
            if field and resolved_fields.get(field) is not None:
                if gold_fields.get(field) != resolved_fields.get(field):
                    return "CURRENT_VS_HISTORICAL_STATE", f"resolved {field} already differs from gold; relation compiler follows wrong state"
                return "ATTRIBUTE_TO_RELATION_COMPILATION", f"resolved {field} is available but {relation_type} is absent"
        return "RELATION_SUPPRESSION", "expected relation is absent and no resolved field supports emission"

    if extra:
        if any(item[0] == "CHANGED_FROM" for item in extra):
            return "TRANSITION_COMPILATION", "transition relation emitted without an aligned expected transition"
        for relation_type, target, value in extra:
            field = DERIVED.get(relation_type)
            if field:
                if resolved_fields.get(field) is not None and str(resolved_fields.get(field)) != str(value):
                    return "RELATION_NORMALIZATION", f"{relation_type} value conflicts with resolved {field}"
                if gold_fields.get(field) is None or resolved_fields.get(field) is None:
                    return "RELATION_OWNER_SELECTION", f"{relation_type} emitted without a compatible owned attribute"
                if gold_fields.get(field) != resolved_fields.get(field):
                    return "CURRENT_VS_HISTORICAL_STATE", f"{relation_type} reflects a non-current resolved state"
        return "RELATION_SUPPRESSION", "relation emitted although gold has no admissible relation"

    return "RELATION_NORMALIZATION", "relation set differs only by value/endpoint normalization"


def _audit_findings() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for dataset, directory in TRACE_SETS.items():
        for path in sorted(directory.glob("*.json")):
            trace = _load(path)
            relation_mismatches = [item for item in trace.get("mismatches", ()) if item.get("stage") == "generated_relations"]
            if not relation_mismatches:
                continue
            resolved_snapshot = next(item for item in trace["snapshots"] if item["stage"] == "resolved_semantics")
            gold_snapshot = next(item for item in trace["snapshots"] if item["stage"] == "gold")
            resolved_mentions = resolved_snapshot.get("payload", {}).get("mentions", [])
            gold_mentions = gold_snapshot.get("payload", {}).get("mentions", [])
            for mismatch in relation_mismatches:
                mention = mismatch.get("details", {}).get("mention")
                resolved = next((item for item in resolved_mentions if item.get("surface") == mention), resolved_mentions[0] if resolved_mentions else {})
                gold = next((item for item in gold_mentions if item.get("surface") == mention), gold_mentions[0] if gold_mentions else {})
                expected = mismatch.get("expected", [])
                actual = mismatch.get("actual", [])
                category, reason = _classify(expected, actual, resolved, gold)
                actual_relation = actual[0] if actual else {}
                expected_relation = expected[0] if expected else {}
                findings.append({
                    "dataset": dataset,
                    "case_id": trace["case_id"],
                    "trace": str(path),
                    "source_mention": mention,
                    "resolved_attributes": resolved.get("fields", {}),
                    "expected_relations": expected,
                    "produced_relations": actual,
                    "owner_expected": str(gold.get("concept_id", "")).split(".", 1)[0] or None,
                    "owner_produced": actual_relation.get("source"),
                    "historical_current": {
                        "expected_temporality": gold.get("fields", {}).get("temporality"),
                        "resolved_temporality": resolved.get("fields", {}).get("temporality"),
                        "expected_status": gold.get("fields", {}).get("status"),
                        "resolved_status": resolved.get("fields", {}).get("status"),
                    },
                    "relation_type": expected_relation.get("relation_type") or actual_relation.get("relation_type"),
                    "relation_endpoint": expected_relation.get("target") or actual_relation.get("target"),
                    "relation_provenance": {
                        "expected": gold.get("relation_provenance", {}),
                        "produced": [item.get("provenance", {}) for item in actual],
                    },
                    "category": category,
                    "reason": reason,
                    "confidence": mismatch.get("confidence"),
                })
    return findings


WRITERS = [
    {
        "writer_id": "RW-01",
        "file": "labs/terminology_benchmark/context_safety.py",
        "lines": "387-405",
        "component": "local semantics",
        "classification": "LOCAL_CANDIDATE_PRODUCER",
        "operation": "creates initial HAS_DOSE/HAS_FREQUENCY/HAS_ROUTE/HAS_LATERALITY/DISCONTINUED_AT projection relations",
        "mutation": "creates",
        "competes_with": ["RW-02", "RW-03", "RW-04", "RW-05", "RW-06"],
    },
    {
        "writer_id": "RW-02",
        "file": "labs/terminology_benchmark/clinical_conversational_semantics.py",
        "lines": "747-814",
        "component": "ClinicalRelationResolver",
        "classification": "CONTEXT_RESOLVER",
        "operation": "compiles attribute attachments, CHANGED_FROM and REFERS_TO; includes HAS_STATUS/EXPERIENCER_OF",
        "mutation": "creates",
        "competes_with": ["RW-01", "RW-03", "RW-04", "RW-05", "RW-06"],
    },
    {
        "writer_id": "RW-03",
        "file": "labs/terminology_benchmark/cross_segment_context.py",
        "lines": "178-191",
        "component": "cross-segment resolver",
        "classification": "CONTEXT_RESOLVER",
        "operation": "synthesizes DISCONTINUED_AT when status is discontinued",
        "mutation": "creates",
        "competes_with": ["RW-01", "RW-02", "RW-04", "RW-05", "RW-06"],
    },
    {
        "writer_id": "RW-04",
        "file": "labs/terminology_benchmark/cross_segment_context.py",
        "lines": "841-976",
        "component": "transition resolver seam",
        "classification": "CONTEXT_RESOLVER",
        "operation": "calls ClinicalRelationResolver and appends transition relations into provenance['projection']['relations']",
        "mutation": "creates and mutates",
        "competes_with": ["RW-01", "RW-02", "RW-03", "RW-05", "RW-06"],
    },
    {
        "writer_id": "RW-05",
        "file": "labs/terminology_benchmark/clinical_projection.py",
        "lines": "53-175",
        "component": "ClinicalRelationMaterializer",
        "classification": "PROJECTION_WRITER",
        "operation": "normalizes, suppresses stale relations, deduplicates and derives current attribute relations",
        "mutation": "creates, suppresses and rewrites",
        "competes_with": ["RW-01", "RW-02", "RW-03", "RW-04", "RW-06"],
    },
    {
        "writer_id": "RW-06",
        "file": "labs/terminology_benchmark/clinical_conversational_semantics.py",
        "lines": "178-257",
        "component": "AuthoritativeProjectionWriter",
        "classification": "PROJECTION_WRITER",
        "operation": "replaces final result fields and serializes resolved_relations into final projection",
        "mutation": "materializes final set",
        "competes_with": ["RW-01", "RW-02", "RW-03", "RW-04", "RW-05"],
    },
]


def _writer_inventory_md() -> str:
    lines = [
        "# Relation Writer Inventory", "", "Status: **HUMAN GATE — inventory only**", "",
        "The inventory is static and was produced without executing the resolver.", "",
        f"- relation writer sites: `{len(WRITERS)}`",
        "- competing relation-producing/mutating components: `5`",
        "- relation rehydration boundary: `cross_segment_context.py:154-167`",
        "- duplicated/competing vocabulary observed: `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_LATERALITY`, `DISCONTINUED_AT`, `CHANGED_FROM`",
        "",
        "| ID | Component | Classification | Operation | Mutation |",
        "|---|---|---|---|---|",
    ]
    for item in WRITERS:
        lines.append(f"| {item['writer_id']} | `{item['file']}:{item['lines']}` / {item['component']} | {item['classification']} | {item['operation']} | {item['mutation']} |")
    lines.extend([
        "", "## Architectural observations", "",
        "1. Local projection creates relations before context resolution has authoritative ownership.",
        "2. Transition handling invokes a second relation resolver and mutates the projection list after local output.",
        "3. Cross-segment status handling has a dedicated relation creation path.",
        "4. ClinicalRelationMaterializer both suppresses and reconstructs relations, while AuthoritativeProjectionWriter serializes another relation set.",
        "5. Provenance can be rewritten at the materializer boundary, so relation source ownership is not established once at a single compiler boundary.",
        "",
        "Conclusion: the current system has multiple relation authorities and post-resolution mutation points. This supports evaluating R2, but does not by itself prove that upstream reference/state errors disappear.",
        "",
    ])
    return "\n".join(lines)


def _architecture_report(findings: list[dict[str, Any]]) -> str:
    by_dataset = Counter(item["dataset"] for item in findings)
    by_category = Counter(item["category"] for item in findings)
    dataset_category: dict[str, Counter[str]] = defaultdict(Counter)
    for item in findings:
        dataset_category[item["dataset"]][item["category"]] += 1
    lines = [
        "# D1/D2 Relation Semantics Architecture Audit", "", "Status: **HUMAN GATE — no repair implemented**", "",
        "Scope: frozen D1/D2 traces only. D1 and D2 were not rerun; resolver, policy, corpus and gold were not modified by this audit.", "",
        "## Generated-relation findings", "",
        f"- D1 relation-first cases/findings: `{len({item['case_id'] for item in findings if item['dataset'] == 'D1'})}` cases / `{sum(value for key, value in dataset_category['D1'].items())}` findings",
        f"- D2 relation-first cases/findings: `{len({item['case_id'] for item in findings if item['dataset'] == 'D2'})}` cases / `{sum(value for key, value in dataset_category['D2'].items())}` findings",
        "",
        "| Category | D1 | D2 | Total |",
        "|---|---:|---:|---:|",
    ]
    for category in sorted(by_category):
        lines.append(f"| {category} | {dataset_category['D1'][category]} | {dataset_category['D2'][category]} | {by_category[category]} |")
    lines.extend([
        "", "## Pattern interpretation", "",
        "- `ATTRIBUTE_TO_RELATION_COMPILATION`: resolved attributes exist but the derived HAS_* relation is absent or stale. This is the clearest compiler-boundary class.",
        "- `TRANSITION_COMPILATION`: CHANGED_FROM is missing or emitted without a coherent current transition.",
        "- `CURRENT_VS_HISTORICAL_STATE`: the resolved state already differs from gold, and relation output follows that wrong state. A compiler alone cannot repair this upstream semantic error.",
        "- `RELATION_OWNER_SELECTION`: a relation is emitted for an incompatible owner or entity type.",
        "- `RELATION_NORMALIZATION`: same relation family has a conflicting value/representation, including local and resolved values coexisting.",
        "- `RELATION_DUPLICATION`: duplicate relation keys appear in the expected or produced set; several D1/D2 discontinued findings are expected-side explicit-plus-derived duplication.",
        "- `RELATION_SUPPRESSION`: an expected relation is absent without sufficient resolved evidence to attribute the loss to a compiler-only omission.",
        "",
        "## Writer topology", "",
        "The writer inventory identifies six relation-writing sites across five competing components. Relation creation occurs both before and after context resolution, and transition code mutates an existing projection relation list. This is inconsistent with a single immutable relation authority.",
        "",
        "## Recommendation", "",
        "**R2 — consolidate writers in a single ClinicalRelationCompiler** is recommended for the relation subsystem, with an explicit limitation: it should be proposed and tested as a boundary consolidation, not assumed to solve the 14 D2 prediction/semantic indeterminate cases or upstream state errors.",
        "",
        "R1 is insufficient because the same relation vocabulary is produced and mutated in multiple components. R3 is not yet justified because the traces do not prove that the relation representation itself cannot express the required semantics. R4 is unsupported: G4 remains zero and no external capability evidence exists.",
        "",
    ])
    return "\n".join(lines)


def _compiler_proposal(findings: list[dict[str, Any]]) -> str:
    categories = Counter(item["category"] for item in findings)
    return "\n".join([
        "# Clinical Relation Compiler Proposal", "", "Status: **PROPOSAL ONLY — not implemented**", "",
        "## Recommendation", "",
        "R2 — consolidate relation writers in one deterministic compiler boundary.", "",
        "The proposal is supported by the writer inventory and the repeated D1/D2 relation-first findings. It is not authorization for a repair or a resolver redesign.", "",
        "## Proposed contract", "",
        "```text",
        "ResolvedClinicalSemantics",
        "  ├── resolved_mentions",
        "  ├── resolved_attributes",
        "  ├── ownership",
        "  ├── current/historical state",
        "  ├── transitions",
        "  └── provenance",
        "          ↓",
        "ClinicalRelationCompiler.compile()",
        "          ↓",
        "immutable ClinicalRelationSet",
        "          ↓",
        "ClinicalProjection",
        "```", "",
        "The compiler must be the only component allowed to create the final relation set. Local semantics may create candidates, but not final relations. Transition detection may produce transition evidence, but not append directly to projection. Projection may serialize the immutable set, but not infer or mutate relations.", "",
        "## Inputs", "",
        "- resolved mentions and stable mention IDs",
        "- resolved attributes with exactly one owner",
        "- owner/entity type",
        "- current versus historical state",
        "- transition evidence, including previous values",
        "- field and event provenance",
        "",
        "## Output rules", "",
        "- emit current `HAS_DOSE`, `HAS_FREQUENCY`, `HAS_ROUTE`, `HAS_LATERALITY` only when owner/type and current value are valid;",
        "- emit `CHANGED_FROM` only from explicit transition evidence;",
        "- emit `DISCONTINUED_AT` only from current medication lifecycle state plus event provenance;",
        "- deduplicate by semantic relation key;",
        "- reject incompatible owner/type relations;",
        "- bind provenance during compilation and make the output immutable;",
        "- never fall back to local relation output after compilation.",
        "",
        "## What this would and would not eliminate", "",
        f"The audit found `{categories['ATTRIBUTE_TO_RELATION_COMPILATION']}` attribute-to-relation findings, `{categories['TRANSITION_COMPILATION']}` transition findings, `{categories['RELATION_OWNER_SELECTION']}` owner-selection findings, `{categories['RELATION_NORMALIZATION']}` normalization findings and `{categories['RELATION_DUPLICATION']}` duplication findings across D1/D2 relation-first traces.",
        "",
        "A single compiler should structurally eliminate competing-writer behavior, stale local relation survival, post-resolution append races and compiler-side provenance drift. It will not by itself correct a wrong resolved dose/status/temporality or a missing antecedent; those remain upstream semantic evidence and must be tested separately.",
        "",
        "## Required future validation", "",
        "1. Freeze a new diagnostic set; do not rerun D1/D2.",
        "2. Compare compiler input truth with gold before judging compiler output.",
        "3. Require immutable relation-set hash, one owner per attribute, unique endpoints and provenance completeness.",
        "4. Report compiler-boundary failures separately from upstream resolved-semantics failures.",
        "5. Keep the 14 D1/D2 prediction indeterminates outside repair authorization until Trace v2 or a new diagnostic set identifies their first divergence.",
        "",
        "Next gate: human authorization is required before implementing the compiler.",
        "",
    ])


def main() -> None:
    findings = _audit_findings()
    matrix = {
        "status": "HUMAN_GATE",
        "scope": "D1/D2 frozen traces, generated_relations first-divergence findings",
        "d1_rerun": False,
        "d2_rerun": False,
        "resolver_modified": False,
        "policy_modified": False,
        "findings_total": len(findings),
        "by_dataset": dict(Counter(item["dataset"] for item in findings)),
        "by_category": dict(Counter(item["category"] for item in findings)),
        "dataset_category": {dataset: dict(Counter(item["category"] for item in findings if item["dataset"] == dataset)) for dataset in ("D1", "D2")},
        "findings": findings,
        "writer_inventory": {
            "relation_writer_sites": len(WRITERS),
            "competing_components": 5,
            "duplicated_vocabularies": sorted({"HAS_DOSE", "HAS_FREQUENCY", "HAS_LATERALITY", "DISCONTINUED_AT", "CHANGED_FROM"}),
        },
        "recommendation": "R2",
        "recommendation_options": {
            "R1": "maintain architecture and fix local bugs",
            "R2": "consolidate writers in a single compiler",
            "R3": "redesign representation model",
            "R4": "external capability required",
        },
    }
    (RESULTS / "RELATION_FAILURE_PATTERN_MATRIX.json").write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DOCS / "RELATION_WRITER_INVENTORY.md").write_text(_writer_inventory_md(), encoding="utf-8")
    (DOCS / "D1_D2_RELATION_ARCHITECTURE_AUDIT.md").write_text(_architecture_report(findings), encoding="utf-8")
    (DOCS / "CLINICAL_RELATION_COMPILER_PROPOSAL.md").write_text(_compiler_proposal(findings), encoding="utf-8")
    print(json.dumps({"status": "AUDIT_COMPLETE", "findings": len(findings), "by_dataset": matrix["by_dataset"], "by_category": matrix["by_category"], "recommendation": "R2", "resolver_modified": False, "d1_d2_rerun": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
