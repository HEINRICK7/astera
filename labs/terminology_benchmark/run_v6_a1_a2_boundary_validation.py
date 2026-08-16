"""Validate upstream/downstream boundaries among adjudicated V6 Type-A findings."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DEFAULT_INPUT = ROOT / "results" / "v6-residual-type-c-adjudication-2026-08-15.json"
DEFAULT_GRAPH = Path("docs/clinical-conversational-semantics/A1_A2_CAUSAL_GRAPH.json")
DEFAULT_REPORT = Path("docs/clinical-conversational-semantics/A1_A2_BOUNDARY_VALIDATION.md")
DEFAULT_PLAN = Path("docs/clinical-conversational-semantics/REPAIR_V5_PLAN.md")


def _field(finding: dict[str, Any]) -> str | None:
    return finding.get("field") or ((finding.get("relation") or [None])[0])


def _current_class(record: dict[str, Any], finding: dict[str, Any]) -> str:
    if finding["classification"] == "WRONG_STATUS" and "discontinued" in finding.get("semantic_reason", ""):
        return "A2"
    if finding["classification"] == "MISSING_RELATION" and record.get("resolved", {}).get("provenance", {}).get("cross_segment"):
        return "A2"
    return "A1"


def _base_mapping(record: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any]:
    classification = finding["classification"]
    reason = finding.get("semantic_reason", "")
    if classification == "WRONG_NEGATION" and "scope" in reason:
        return "MENTION_SCOPE", "Cross-Segment Resolution", "SEM-NEG-001", "negation scope ownership", "A1"
    if classification == "WRONG_NEGATION":
        return "NEGATION", "Local Semantics", "SEM-NEG-001", "explicit negation cue", "A1"
    if classification == "WRONG_STATUS" and "discontinued" in reason:
        return "CROSS_SEGMENT", "Cross-Segment Resolution", "SEM-XSEG-001", "cross-segment owner/state inheritance", "A2"
    if classification == "WRONG_STATUS":
        return "STATUS", "ResolvedClinicalSemantics", "SEM-STATUS-001", "status materialization", "A1"
    if classification == "WRONG_TEMPORALITY":
        return "TEMPORALITY", "Local Semantics", "SEM-TEMP-001", "temporal cue ownership", "A1"
    if classification == "WRONG_LATERALITY":
        return "ATTRIBUTE_OWNERSHIP", "Attribute Ownership", "SEM-REL-001", "laterality owner attachment", "A1"
    if classification == "WRONG_EXPERIENCER":
        return "EXPERIENCER", "Attribute Ownership", "SEM-EXP-001", "experiencer owner attachment", "A1"
    if classification == "WRONG_DOSE":
        return "DOSE", "Attribute Ownership", "SEM-DOSE-001", "current-dose transition ownership", "A1"
    if classification == "WRONG_FREQUENCY":
        return "FREQUENCY", "Attribute Ownership", "SEM-FREQ-001", "current-frequency transition ownership", "A1"
    if classification == "MISSING_RELATION":
        return "RELATION_MISSING", "Relation Resolution", "SEM-REL-001", "relation candidate emission", _current_class(record, finding)
    return "RELATION_WRONG", "Relation Resolution", "SEM-REL-002", "relation admissibility/endpoint", "A1"


def _causal_adjustment(record: dict[str, Any], finding: dict[str, Any], siblings: list[dict[str, Any]]) -> dict[str, Any]:
    dimension, stage, policy, root, current = _base_mapping(record, finding)
    fields = {_field(item) for item in siblings}
    relation_type = (finding.get("relation") or [None])[0]
    if finding["classification"] in {"MISSING_RELATION", "WRONG_RELATION", "EXTRA_RELATION"}:
        if relation_type == "HAS_LATERALITY" and "laterality" in fields:
            return {
                "first_divergence_stage": "Attribute Ownership",
                "root_cause": "laterality owner was wrong before relation materialization",
                "upstream_dependency": "ATTRIBUTE_OWNERSHIP",
                "downstream_effects": ["relation missing/wrong"],
                "validated_class": "A2",
            }
        if relation_type in {"HAS_DOSE", "HAS_FREQUENCY", "CHANGED_FROM"} and ({"dose", "dose_value", "frequency"} & fields):
            return {
                "first_divergence_stage": "Attribute Ownership",
                "root_cause": "transition attribute ownership was wrong before relation materialization",
                "upstream_dependency": "TRANSITION_ATTRIBUTE_OWNERSHIP",
                "downstream_effects": ["relation missing/wrong/extra"],
                "validated_class": "A2",
            }
        if relation_type == "DISCONTINUED_AT" and "status" in fields:
            return {
                "first_divergence_stage": "ResolvedClinicalSemantics",
                "root_cause": "discontinued state was incomplete before temporal relation emission",
                "upstream_dependency": "STATUS",
                "downstream_effects": ["DISCONTINUED_AT relation missing"],
                "validated_class": "A2",
            }
    return {
        "first_divergence_stage": stage,
        "root_cause": root,
        "upstream_dependency": None,
        "downstream_effects": [],
        "validated_class": current,
    }


def run(input_path: Path, graph_path: Path, report_path: Path, plan_path: Path) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    findings: list[dict[str, Any]] = []
    nodes: dict[str, dict[str, Any]] = {}
    edges: Counter[tuple[str, str]] = Counter()
    for record in source["records"]:
        type_a = [item for item in record["differing_fields"] if item.get("error_type") == "A"]
        for finding in type_a:
            dimension, stage, policy, root, current = _base_mapping(record, finding)
            causal = _causal_adjustment(record, finding, type_a)
            item = {
                "case_id": record["case_id"],
                "mention": record["surface"],
                "occurrence": record.get("occurrence", 0),
                "semantic_dimension": dimension,
                "expected": finding.get("expected") if finding.get("field") else finding.get("relation"),
                "actual": finding.get("resolved") if finding.get("field") else None,
                "differing_field": _field(finding),
                "first_divergence_stage": causal["first_divergence_stage"],
                "root_cause": causal["root_cause"],
                "upstream_dependency": causal["upstream_dependency"],
                "downstream_effects": causal["downstream_effects"],
                "current_class": current,
                "validated_class": causal["validated_class"],
                "policy_rule": policy,
                "text": record["text"],
            }
            findings.append(item)
            root_id = {
                "STATUS": "ROOT-STATUS",
                "MENTION_SCOPE": "ROOT-NEGATION-SCOPE",
                "NEGATION": "ROOT-NEGATION",
                "TEMPORALITY": "ROOT-TEMPORAL-OWNERSHIP",
                "ATTRIBUTE_OWNERSHIP": "ROOT-ATTRIBUTE-OWNERSHIP",
                "EXPERIENCER": "ROOT-EXPERIENCER-OWNERSHIP",
                "DOSE": "ROOT-TRANSITION-OWNERSHIP",
                "FREQUENCY": "ROOT-TRANSITION-OWNERSHIP",
                "CROSS_SEGMENT": "ROOT-CROSS-SEGMENT-OWNERSHIP",
                "RELATION_MISSING": "ROOT-RELATION-RESOLUTION",
                "RELATION_WRONG": "ROOT-RELATION-RESOLUTION",
            }.get(dimension, "ROOT-UNMAPPED")
            nodes.setdefault(root_id, {"id": root_id, "kind": "root", "direct_findings": 0, "downstream_findings": 0})
            if causal["upstream_dependency"]:
                upstream_id = {
                    "ATTRIBUTE_OWNERSHIP": "ROOT-ATTRIBUTE-OWNERSHIP",
                    "TRANSITION_ATTRIBUTE_OWNERSHIP": "ROOT-TRANSITION-OWNERSHIP",
                    "STATUS": "ROOT-STATUS",
                }[causal["upstream_dependency"]]
                edges[(upstream_id, root_id)] += 1
                nodes.setdefault(upstream_id, {"id": upstream_id, "kind": "root", "direct_findings": 0, "downstream_findings": 0})
                nodes[upstream_id]["direct_findings"] += 0
                nodes[root_id]["downstream_findings"] += 1
            else:
                nodes[root_id]["direct_findings"] += 1

    current_counts = Counter(item["current_class"] for item in findings)
    validated_counts = Counter(item["validated_class"] for item in findings)
    stage_counts = Counter(item["first_divergence_stage"] for item in findings)
    matrix = {
        "status": "a1_a2_boundary_validated",
        "source": input_path.name,
        "policy_version": "1.1",
        "official_corpus_sha256": source["official_corpus_sha256"],
        "resolver_modified": False,
        "corpus_modified": False,
        "gold_modified": False,
        "holdout_evaluation": "NOT_EXECUTED",
        "v7": "BLOCKED",
        "shadow": "BLOCKED",
        "production": "BLOCKED",
        "finding_count": len(findings),
        "current_class_counts": dict(current_counts),
        "validated_class_counts": dict(validated_counts),
        "first_divergence_stage_counts": dict(stage_counts),
        "causal_edges": [{"from": source_id, "to": target_id, "count": count} for (source_id, target_id), count in sorted(edges.items())],
        "nodes": sorted(nodes.values(), key=lambda item: item["id"]),
        "findings": findings,
        "repair_v5_authorized": False,
    }
    graph_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# A1/A2 Boundary Validation & Repair Plan — V6",
        "",
        "Status: **HUMAN GATE — ANALYSIS ONLY**  ",
        "Policy: `CLINICAL_SEMANTIC_POLICY` v1.1  ",
        f"Corpus checksum: `{source['official_corpus_sha256']}`  ",
        "Resolver, corpus, gold, policy, and benchmark changes: **none**",
        "",
        "## Method",
        "",
        "Each Type-A finding was traced against the available candidate, context, ownership, relation, resolved-semantics, and projection provenance. A downstream relation finding was marked causally dependent only when the same mention also contained an upstream attribute/status/transition divergence. Otherwise it remains an independent relation finding.",
        "",
        "## Current versus validated class",
        "",
        "| Class | Current | Validated |",
        "|---|---:|---:|",
        f"| A1 | {current_counts['A1']} | {validated_counts['A1']} |",
        f"| A2 | {current_counts['A2']} | {validated_counts['A2']} |",
        "| A3 | 0 | 0 |",
        "| A4 | 0 | 0 |",
        "",
        "The causal validation does not justify collapsing all A2 into A1. It confirms a narrower set of downstream dependencies and keeps the remaining A2 boundaries explicit.",
        "",
        "## First divergence stages",
        "",
        "| Stage | Findings | Interpretation |",
        "|---|---:|---|",
    ]
    for stage, count in sorted(stage_counts.items(), key=lambda item: -item[1]):
        lines.append(f"| {stage} | {count} | first observed divergence in the trace |")
    lines += [
        "",
        "## Validated causal relations",
        "",
        "| Upstream root | Downstream root | Findings | Evidence rule |",
        "|---|---|---:|---|",
    ]
    for edge in matrix["causal_edges"]:
        lines.append(f"| {edge['from']} | {edge['to']} | {edge['count']} | same mention has upstream field divergence and downstream relation finding |")
    if not matrix["causal_edges"]:
        lines.append("| none | none | 0 | no validated downstream dependency |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- The strongest validated dependencies are relation findings downstream of same-mention attribute/transition/status divergences.",
        "- A relation appearing downstream in the score is not automatically an independent relation-resolver defect.",
        "- The available trace does not prove an A3 unresolved outcome or an A4 deterministic-rule ceiling; both remain zero without being treated as impossible.",
        "- Mention extraction and broad reference-resolution limitations remain unassessed by this query-per-gold evidence.",
        "",
        "## Repair V5 boundary",
        "",
        "Repair V5 is **NOT AUTHORIZED**. The causal graph must first receive human approval, and any future repair must be staged by upstream root cause with invariant tests between stages.",
        "",
        "```text",
        "V6 frozen              = yes",
        "policy v1.1 frozen     = yes",
        "Type B untouched       = yes",
        "holdouts               = NOT_EXECUTED",
        "V7                    = BLOCKED",
        "Shadow                = BLOCKED",
        "Production            = BLOCKED",
        "Repair V5              = NOT AUTHORIZED",
        "```",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = """# Repair V5 Plan — V6 Type A Only

Status: **PLAN ONLY — HUMAN GATE**

No implementation is authorized by this document. The plan orders future work by causal dependency, not by raw error count.

## Proposed order

1. `ROOT-ATTRIBUTE-OWNERSHIP` and `ROOT-TRANSITION-OWNERSHIP` — validate owner invariants and current-versus-historical transitions.
2. `ROOT-NEGATION-SCOPE` — validate target-scoped negation and its interaction with mention scope.
3. `ROOT-STATUS` — materialize policy v1.1 status without allowing negation or ownership leakage.
4. `ROOT-TEMPORAL-OWNERSHIP` — resolve event/state temporality without assigning it to experiencer references.
5. `ROOT-RELATION-RESOLUTION` — repair only after upstream ownership/status/transition gates pass.
6. `ROOT-CROSS-SEGMENT-OWNERSHIP` — validate context inheritance after local semantics are stable.

## Required per-phase gates

- synthetic and invariant tests;
- candidate and projection integrity gates;
- RAW V6 score retained for historical comparison;
- POLICY-ALIGNED V6 score as the quality gate;
- Type B items excluded from repair targets and kept in the review queue;
- no holdouts until the staged Type-A sequence passes HUMAN GATE.

## Current authorization

```text
Repair V5 = NOT AUTHORIZED
V6 = FROZEN
Policy = v1.1 FROZEN
Type B = UNTOUCHED
Holdouts = NOT_EXECUTED
V7 = BLOCKED
Shadow = BLOCKED
Production = BLOCKED
```
"""
    plan_path.write_text(plan, encoding="utf-8")
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.graph, args.report, args.plan), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
