"""Decompose adjudicated V6 Type-A findings without changing production code."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DEFAULT_INPUT = ROOT / "results" / "v6-residual-type-c-adjudication-2026-08-15.json"
DEFAULT_JSON = Path("docs/clinical-conversational-semantics/TYPE_A_ROOT_CAUSE_MATRIX.json")
DEFAULT_MD = Path("docs/clinical-conversational-semantics/TYPE_A_POST_V4_STRATEGY.md")


def _mention_key(record: dict[str, Any]) -> str:
    return json.dumps([record["case_id"], record["surface"], record.get("occurrence", 0)], ensure_ascii=False)


def _is_cross_segment(record: dict[str, Any]) -> bool:
    return bool(record.get("resolved", {}).get("provenance", {}).get("cross_segment"))


def _mapping(record: dict[str, Any], finding: dict[str, Any]) -> dict[str, Any]:
    classification = finding["classification"]
    reason = finding.get("semantic_reason", "")
    cross_segment = _is_cross_segment(record)
    if classification == "WRONG_NEGATION" and "scope" in reason:
        return {
            "semantic_dimension": "MENTION_SCOPE",
            "current_component": "CrossSegmentContextResolver negation scope",
            "recommended_component": "target-scoped negation resolver",
            "policy_rule": "SEM-NEG-001",
            "repair_class": "A1",
            "repairability": "deterministic",
            "risk": "medium",
        }
    if classification == "WRONG_NEGATION":
        return {
            "semantic_dimension": "NEGATION",
            "current_component": "NieDEPtBrSafetyRules negation cues",
            "recommended_component": "local negation target matcher",
            "policy_rule": "SEM-NEG-001",
            "repair_class": "A1",
            "repairability": "deterministic",
            "risk": "medium",
        }
    if classification == "WRONG_STATUS" and "discontinued" in reason:
        return {
            "semantic_dimension": "CROSS_SEGMENT",
            "current_component": "CrossSegmentContextResolver owner/state inheritance",
            "recommended_component": "typed owner-gated state inheritance",
            "policy_rule": "SEM-XSEG-001",
            "repair_class": "A2",
            "repairability": "architectural boundary change",
            "risk": "high",
        }
    if classification == "WRONG_STATUS":
        return {
            "semantic_dimension": "STATUS",
            "current_component": "status resolution/materialization path",
            "recommended_component": "policy-backed status projection",
            "policy_rule": "SEM-STATUS-001",
            "repair_class": "A1",
            "repairability": "deterministic",
            "risk": "medium",
        }
    if classification == "WRONG_TEMPORALITY":
        return {
            "semantic_dimension": "TEMPORALITY",
            "current_component": "NieDEPtBrSafetyRules temporal cue resolver",
            "recommended_component": "event/state temporal ownership resolver",
            "policy_rule": "SEM-TEMP-001",
            "repair_class": "A1",
            "repairability": "deterministic for explicit cues",
            "risk": "high",
        }
    if classification == "WRONG_EXPERIENCER":
        return {
            "semantic_dimension": "EXPERIENCER",
            "current_component": "NieDEPtBrSafetyRules experiencer cue resolver",
            "recommended_component": "experiencer owner resolver",
            "policy_rule": "SEM-EXP-001",
            "repair_class": "A1",
            "repairability": "deterministic",
            "risk": "medium",
        }
    if classification == "WRONG_LATERALITY":
        return {
            "semantic_dimension": "ATTRIBUTE_OWNERSHIP",
            "current_component": "laterality attachment resolver",
            "recommended_component": "nearest-compatible owner with typed scope",
            "policy_rule": "SEM-REL-001",
            "repair_class": "A1",
            "repairability": "deterministic for explicit cues",
            "risk": "medium",
        }
    if classification == "WRONG_DOSE":
        return {
            "semantic_dimension": "DOSE",
            "current_component": "dose transition resolver",
            "recommended_component": "current-dose plus CHANGED_FROM transition resolver",
            "policy_rule": "SEM-DOSE-001",
            "repair_class": "A1",
            "repairability": "deterministic for explicit transitions",
            "risk": "high",
        }
    if classification == "WRONG_FREQUENCY":
        return {
            "semantic_dimension": "FREQUENCY",
            "current_component": "frequency transition resolver",
            "recommended_component": "current-frequency plus CHANGED_FROM transition resolver",
            "policy_rule": "SEM-FREQ-001",
            "repair_class": "A1",
            "repairability": "deterministic for explicit transitions",
            "risk": "high",
        }
    if classification == "MISSING_RELATION":
        return {
            "semantic_dimension": "RELATION_MISSING",
            "current_component": "ClinicalRelationResolver / relation projection",
            "recommended_component": "relation candidate emission and endpoint validation",
            "policy_rule": "SEM-REL-001",
            "repair_class": "A2" if cross_segment else "A1",
            "repairability": "deterministic relation emission; integration-sensitive",
            "risk": "high",
        }
    if classification in {"WRONG_RELATION", "EXTRA_RELATION"}:
        return {
            "semantic_dimension": "RELATION_WRONG",
            "current_component": "ClinicalRelationResolver / relation projection",
            "recommended_component": "current-vs-historical relation admissibility gate",
            "policy_rule": "SEM-REL-002",
            "repair_class": "A1",
            "repairability": "deterministic under frozen relation policy",
            "risk": "high",
        }
    return {
        "semantic_dimension": "REFERENCE_RESOLUTION",
        "current_component": "unmapped",
        "recommended_component": "human review",
        "policy_rule": "unmapped",
        "repair_class": "A4",
        "repairability": "unknown",
        "risk": "high",
    }


def run(input_path: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    findings: list[dict[str, Any]] = []
    for record in source["records"]:
        for finding in record["differing_fields"]:
            if finding.get("error_type") != "A":
                continue
            mapping = _mapping(record, finding)
            findings.append({
                "case_id": record["case_id"],
                "surface": record["surface"],
                "occurrence": record.get("occurrence", 0),
                "text": record["text"],
                "segments": record.get("segments", []),
                "classification": finding["classification"],
                "field": finding.get("field"),
                "relation": finding.get("relation"),
                "expected": finding.get("expected"),
                "resolved": finding.get("resolved"),
                "root_cause": finding.get("semantic_reason"),
                "confidence": finding.get("confidence"),
                "cross_segment": _is_cross_segment(record),
                **mapping,
            })

    dimensions = [
        "MENTION_EXTRACTION", "MENTION_SCOPE", "REFERENCE_RESOLUTION", "ATTRIBUTE_OWNERSHIP",
        "TEMPORALITY", "STATUS", "NEGATION", "EXPERIENCER", "DOSE", "FREQUENCY",
        "RELATION_MISSING", "RELATION_WRONG", "CROSS_SEGMENT",
    ]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for finding in findings:
        grouped[(finding["semantic_dimension"], finding["root_cause"])].append(finding)
    aggregate: list[dict[str, Any]] = []
    for (dimension, root_cause), items in sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0])):
        aggregate.append({
            "semantic_dimension": dimension,
            "root_cause": root_cause,
            "count": len(items),
            "affected_cases": len({item["case_id"] for item in items}),
            "affected_mentions": len({_mention_key(item) for item in items}),
            "affected_relations": sum(bool(item.get("relation") or item["classification"].endswith("RELATION")) for item in items),
            "policy_rule": items[0]["policy_rule"],
            "current_component": items[0]["current_component"],
            "recommended_component": items[0]["recommended_component"],
            "repair_class": items[0]["repair_class"],
            "repairability": items[0]["repairability"],
            "risk": items[0]["risk"],
            "example_cases": sorted({item["case_id"] for item in items})[:5],
        })

    dimension_counts = Counter(item["semantic_dimension"] for item in findings)
    for dimension in dimensions:
        dimension_counts.setdefault(dimension, 0)
    repair_counts = Counter(item["repair_class"] for item in findings)
    for repair_class in ("A1", "A2", "A3", "A4"):
        repair_counts.setdefault(repair_class, 0)
    root_counts = Counter(item["root_cause"] for item in findings)
    cross_overlay = {
        "findings_with_cross_segment_provenance": sum(item["cross_segment"] for item in findings),
        "affected_cases": len({item["case_id"] for item in findings if item["cross_segment"]}),
        "affected_mentions": len({_mention_key(item) for item in findings if item["cross_segment"]}),
        "note": "overlapping diagnostic dimension; not additive to primary semantic dimensions",
    }
    result = {
        "status": "post_v4_type_a_strategy_analysis",
        "source": input_path.name,
        "policy_version": "1.1",
        "official_corpus_sha256": source["official_corpus_sha256"],
        "corpus_modified": False,
        "gold_modified": False,
        "resolver_modified": False,
        "holdout_evaluation": "NOT_EXECUTED",
        "v7": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
        "total_type_a_findings": len(findings),
        "affected_cases": len({item["case_id"] for item in findings}),
        "affected_mentions": len({_mention_key(item) for item in findings}),
        "repair_class_counts": dict(repair_counts),
        "dimension_counts": dict(sorted(dimension_counts.items())),
        "cross_segment_overlay": cross_overlay,
        "top_root_causes": [{"root_cause": root, "count": count} for root, count in root_counts.most_common(10)],
        "aggregate": aggregate,
        "findings": findings,
        "recommended_next_milestone": "Human review of A1/A2 boundary, then a scoped Type-A repair proposal; do not start Repair V5 yet.",
    }
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Post-V4 Type A Strategy & Error Decomposition",
        "",
        "Status: **HUMAN GATE — ANALYSIS ONLY**  ",
        "Policy: `CLINICAL_SEMANTIC_POLICY` v1.1  ",
        f"Corpus checksum: `{source['official_corpus_sha256']}`  ",
        "Resolver/corpus/gold/policy changes during analysis: **none**",
        "",
        "## Snapshot",
        "",
        f"The adjudicated snapshot contains **{len(findings)} Type A findings**, across **{len({item['case_id'] for item in findings})} cases** and **{len({_mention_key(item) for item in findings})} affected mentions**.",
        "",
        "| Repair class | Count | Interpretation |",
        "|---|---:|---|",
        f"| A1 | {repair_counts['A1']} | Local/deterministic bug |",
        f"| A2 | {repair_counts['A2']} | Architectural/integration boundary |",
        f"| A3 | {repair_counts['A3']} | Should remain unresolved |",
        f"| A4 | {repair_counts['A4']} | Probable deterministic-rule limit |",
        "",
        "## Primary dimension matrix",
        "",
        "Counts are mutually exclusive primary dimensions. Cross-segment is also reported as an overlapping overlay.",
        "",
        "| Dimension | Count | Cases | Mentions | Relations | Policy | Repair class | Risk |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for item in aggregate:
        lines.append(f"| {item['semantic_dimension']} | {item['count']} | {item['affected_cases']} | {item['affected_mentions']} | {item['affected_relations']} | `{item['policy_rule']}` | {item['repair_class']} | {item['risk']} |")
    lines += [
        "",
        "## Top root causes",
        "",
    ]
    for index, item in enumerate(result["top_root_causes"][:5], start=1):
        lines.append(f"{index}. **{item['count']}** — {item['root_cause']}")
    lines += [
        "",
        "## Cross-segment overlay",
        "",
        f"{cross_overlay['findings_with_cross_segment_provenance']} findings affect {cross_overlay['affected_cases']} cases and {cross_overlay['affected_mentions']} mentions through cross-segment provenance. This is an overlapping diagnostic dimension, not an additional bucket.",
        "",
        "## Interpretation",
        "",
        "- A1 dominates the current decomposition: explicit cue, ownership, transition, and relation-admissibility defects appear deterministic under policy v1.1.",
        "- A2 is concentrated in cross-segment state inheritance and relation emission/projection boundaries; it should not be addressed by adding isolated lexical rules.",
        "- A3 and A4 have no findings in this Type-A snapshot. This is not evidence that the deterministic engine has no ceiling; it means the current Type-A set does not prove those classes.",
        "- Mention extraction and reference resolution have no independently measured Type-A findings in this query-per-gold trace; they remain unassessed rather than zero in the broader system.",
        "",
        "## Recommendation and gate",
        "",
        "Recommended next milestone: human review of the A1/A2 boundary followed by a narrowly scoped Type-A repair proposal. Do not start Repair V5 or add a probabilistic provider from this report alone.",
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
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.json, args.markdown), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
