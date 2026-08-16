"""Build the post-holdout root-cause report without rerunning holdouts.

This script consumes only the persisted one-shot holdout result and the frozen
holdout source.  The causal traces are static reconstructions from the stored
fields plus inspected resolver paths; no adapter or benchmark case is run.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
RESULT = ROOT / "results/context-validation-v6-holdout-0056-0058-2026-08-15.json"
SOURCE = ROOT / "results/v6-human-review-micro-expansion-submission-2026-08-15.json"
REPORT_JSON = ROOT / "results/holdout-failure-root-cause-analysis-2026-08-15.json"
REPORT_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/HOLDOUT_FAILURE_ROOT_CAUSE_ANALYSIS.md"


def _load() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_by_id = {item["candidate_id"]: item for item in source}
    return result, source_by_id


def _relation_tuple(items: list[list[str | None]]) -> list[dict[str, str | None]]:
    return [
        {"relation_type": item[0], "target": item[1], "value": item[2]}
        for item in items
    ]


def _trace(case: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    mention = case["mentions"][0]
    aligned = mention["policy_aligned"]
    case_id = case["case_id"]
    segments = [
        {"segment_id": item["segment_id"], "speaker": item["speaker"], "text": item["text"]}
        for item in source["segments"]
    ]

    if case_id == "sim-v6-0057":
        local_mentions = [{"surface": "dor", "concept_id": "symptom.pain", "segment_id": segments[0]["segment_id"]}]
        candidate_attributes = [
            {"field": "laterality", "value": "left", "source_segment_id": segments[1]["segment_id"], "rule": "_last_laterality + continuity attachment"}
        ]
        selected = {"antecedent": "dor", "segment_id": segments[0]["segment_id"], "status": "selected"}
        root_findings = [
            {
                "finding_id": "0057-F1",
                "classification": "RELATION_NOT_GENERATED",
                "generalization_class": "GENERALIZATION_BUG",
                "first_divergence_stage": "Relation Resolution",
                "root_cause": "laterality is attached to the resolved mention, but the continuity path does not create HAS_LATERALITY for a cross-segment attribute-only answer",
                "evidence": [
                    "stored policy-aligned laterality is left",
                    "stored projected relations are empty",
                    "_apply_continuity assigns laterality at cross_segment_context.py:373-381",
                    "_materialize_authoritative reads only candidate_result.provenance['projection']['relations'] at cross_segment_context.py:153-167",
                ],
                "confidence": "high",
            }
        ]
    elif case_id == "sim-v6-0058":
        local_mentions = [{"surface": "metformina", "concept_id": "medication.metformin", "segment_id": segments[0]["segment_id"]}]
        candidate_attributes = [
            {"field": "dose", "value": "850 mg", "source_segment_id": segments[1]["segment_id"], "rule": "_last_dose + continuity attachment"},
            {"field": "dose_value", "value": "850", "source_segment_id": segments[1]["segment_id"], "rule": "_last_dose + continuity attachment"},
            {"field": "dose_unit", "value": "mg", "source_segment_id": segments[1]["segment_id"], "rule": "_last_dose + continuity attachment"},
            {"field": "temporality", "value": "past", "source_segment_id": segments[1]["segment_id"], "cue": "ontem"},
        ]
        selected = {"antecedent": "metformina", "segment_id": segments[0]["segment_id"], "status": "selected"}
        root_findings = [
            {
                "finding_id": "0058-F1",
                "classification": "RELATION_NOT_GENERATED",
                "generalization_class": "GENERALIZATION_BUG",
                "first_divergence_stage": "Relation Resolution",
                "root_cause": "the question-answer dose attachment populates dose fields, but HAS_DOSE is generated only by the local projection or the two-dose transition path; this answer contains one new dose and therefore reaches projection with no relation",
                "evidence": [
                    "stored policy-aligned dose fields are all correct",
                    "stored projected relations are empty",
                    "_apply_continuity assigns dose fields at cross_segment_context.py:383-393",
                    "_augment_transition_relations returns when fewer than two dose values are available, so a single answer dose is not projected",
                ],
                "confidence": "high",
            },
            {
                "finding_id": "0058-F2",
                "classification": "TEMPORAL_OWNERSHIP_FAILURE",
                "generalization_class": "GENERALIZATION_BUG",
                "first_divergence_stage": "Cross-Segment Resolution",
                "root_cause": "the temporal cue ontem is assigned to the medication mention itself, although the approved semantics treat the dose-change event time separately from the current medication state",
                "evidence": [
                    "stored expected temporality is current and actual temporality is past",
                    "_PAST_CUE includes ontem at cross_segment_context.py:49-52",
                    "following-text logic overwrites current with past at cross_segment_context.py:400-402",
                    "dose and active status are otherwise resolved correctly",
                ],
                "confidence": "high",
            },
        ]
    else:
        local_mentions = [{"surface": "diabetes", "concept_id": "condition.diabetes", "segment_id": segments[0]["segment_id"]}]
        candidate_attributes = [
            {"field": "experiencer", "value": "family", "source_segment_id": segments[1]["segment_id"], "rule": "family continuity"},
            {"field": "temporality", "value": "current", "source_segment_id": segments[1]["segment_id"], "rule": "current assertion"},
        ]
        selected = {"antecedent": "diabetes", "segment_id": segments[0]["segment_id"], "status": "selected"}
        root_findings = []

    return {
        "case_id": case_id,
        "text": case["text"],
        "segments": segments,
        "trace_status": "STATIC_RECONSTRUCTION_FROM_CONSUMED_ONE_SHOT_RESULT",
        "local_mentions": local_mentions,
        "candidate_attributes": candidate_attributes,
        "selected_antecedent": selected,
        "resolved_attributes": {
            field: item["actual"] for field, item in aligned["fields"].items()
        },
        "resolved_relations": _relation_tuple(aligned["relations_actual"]),
        "projected_relations": _relation_tuple(aligned["relations_actual"]),
        "evaluated_result": {
            "mention_exact": aligned["mention_exact"],
            "relation_exact": aligned["relation_exact"],
            "attribute_ownership": aligned["attribute_ownership"],
            "provenance_check": aligned["provenance"],
        },
        "expected": {
            "fields": {field: item["expected"] for field, item in aligned["fields"].items()},
            "relations": _relation_tuple(aligned["relations_expected"]),
        },
        "root_findings": root_findings,
    }


def _provenance_audit(result: dict[str, Any]) -> dict[str, Any]:
    failed = [case["case_id"] for case in result["cases"] if not case["mentions"][0]["policy_aligned"]["provenance"]]
    return {
        "observed_check": "0/3",
        "failed_cases": failed,
        "classification": "PROVENANCE_MATERIALIZATION_FAILURE",
        "contributing_evaluator_condition": "HARNESS_NORMALIZATION_MISMATCH",
        "finding_scope": "independent_of_missing_relation_findings",
        "cause": "the holdout provenance contract requires provenance.source_text to equal the full conversation text; the local candidate is built from the target segment and the authoritative materialization preserves that segment-scoped source_text",
        "evidence": [
            "run_holdout_v6.py:_provenance_ok requires source_text == case.text",
            "cross_segment_context.py:_local_result passes target.text to the local adapter",
            "context_safety.py returns source_text=query.text for that localized candidate",
            "AuthoritativeProjectionWriter preserves local_candidate.provenance before adding resolved metadata",
        ],
        "confidence": "high",
        "not_counted_as_relation_cause": True,
        "next_action": "human gate; decide whether provenance should be full-conversation or explicitly segment-scoped before any repair",
    }


def build() -> dict[str, Any]:
    result, source_by_id = _load()
    traces = []
    for case in result["cases"]:
        traces.append(_trace(case, source_by_id[case["case_id"]]))
    findings = [finding for trace in traces for finding in trace["root_findings"]]
    classification_counts = {
        item: sum(finding["classification"] == item for finding in findings)
        for item in (
            "CANDIDATE_MISSING", "ATTRIBUTE_NOT_PROPAGATED", "RELATION_NOT_GENERATED",
            "RELATION_FILTERED", "CROSS_SEGMENT_REFERENCE_FAILURE", "TEMPORAL_OWNERSHIP_FAILURE",
            "PROVENANCE_MATERIALIZATION_FAILURE", "POLICY_MISMATCH",
        )
    }
    return {
        "analysis": "Holdout Failure Root Cause Analysis — Generalization Gap",
        "analysis_date": "2026-08-15",
        "analysis_mode": "static reconstruction; no holdout rerun",
        "input_result": str(RESULT),
        "input_holdout_source": str(SOURCE),
        "holdout_status": {
            "consumed_holdout": True,
            "generalization_evidence": "historical",
            "holdout_rerun": False,
            "holdout_ids": result["holdout_ids"],
            "v6_frozen": True,
            "resolver_policy_corpus_modified": False,
        },
        "aggregate_observed": result["aggregate"],
        "root_cause_summary": {
            "semantic_findings_total": len(findings),
            "generalization_bug_findings": sum(item["generalization_class"] == "GENERALIZATION_BUG" for item in findings),
            "generalization_capability_gap_confirmed": 0,
            "classification_counts": classification_counts,
            "primary_root_causes": [
                "0057: cross-segment laterality attribute is resolved but HAS_LATERALITY is not generated",
                "0058: single answer dose is resolved but HAS_DOSE is not generated",
                "0058: event cue ontem is assigned to medication state temporality",
            ],
            "capability_gap_statement": "No capability gap is proven by these two cases. The existing system identifies the antecedents and values; the observed failures are missing relation materialization and temporal ownership. A future event/state representation may be needed, but that remains a hypothesis, not an authorized repair conclusion.",
        },
        "provenance_audit": _provenance_audit(result),
        "traces": traces,
        "controls": {
            "0056": "semantic pass; retained as a passed historical control, with the same provenance contract failure",
            "relations": "not frozen as a successful generalization capability; V6 relation score does not cover these unseen relation forms",
            "repair_after_holdout": "NOT_AUTHORIZED",
            "v7": "BLOCKED",
            "shadow": "BLOCKED",
            "production": "BLOCKED",
        },
    }


def _md(report: dict[str, Any]) -> str:
    summary = report["root_cause_summary"]
    provenance = report["provenance_audit"]
    lines = [
        "# Holdout Failure Root Cause Analysis — Generalization Gap",
        "",
        "> Status: HUMAN GATE. This is a post-holdout diagnosis only; no resolver repair was authorized or performed.",
        "",
        "## Integrity boundary",
        "",
        "The three cases were executed once and are now consumed holdouts. This report reads the persisted one-shot result and frozen source, then reconstructs the causal path from static code evidence. It does not call the resolver, rerun a holdout, or modify resolver, policy, corpus, gold, or the holdout source.",
        "",
        "- `consumed_holdout = true`",
        "- `generalization_evidence = historical`",
        "- `holdout_rerun = false`",
        "- V6, resolver freeze, and Semantic Policy v1.2 preserved",
        "- Repair after holdout: `NOT_AUTHORIZED`",
        "- V7, Shadow Integration, and Production: `BLOCKED`",
        "",
        "## Diagnosis",
        "",
        f"The semantic failures are {summary['semantic_findings_total']}: {summary['generalization_bug_findings']} are classified as `GENERALIZATION_BUG`, and no `GENERALIZATION_CAPABILITY_GAP` is proven. The system found the relevant antecedents and values; the unseen-path failures occur after candidate/reference success, in relation materialization and temporal ownership.",
        "",
        "| Finding | First divergence | Classification | Generalization class | Confidence |",
        "|---|---|---|---|---|",
    ]
    for trace in report["traces"]:
        for finding in trace["root_findings"]:
            lines.append(f"| {finding['finding_id']} ({trace['case_id']}) | {finding['first_divergence_stage']} | `{finding['classification']}` | `{finding['generalization_class']}` | {finding['confidence']} |")
    lines += [
        "",
        "### Classification counts",
        "",
        "| Class | Count |",
        "|---|---:|",
    ]
    for key, value in summary["classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines += [
        "",
        "## Case traces",
        "",
    ]
    for trace in report["traces"]:
        lines += [f"### {trace['case_id']}", "", f"`{trace['text']}`", "", "**Segments**", ""]
        for segment in trace["segments"]:
            lines.append(f"- `{segment['segment_id']}` ({segment['speaker']}): {segment['text']}")
        lines += ["", f"- Local mentions: `{json.dumps(trace['local_mentions'], ensure_ascii=False)}`", f"- Candidate attributes: `{json.dumps(trace['candidate_attributes'], ensure_ascii=False)}`", f"- Selected antecedent: `{json.dumps(trace['selected_antecedent'], ensure_ascii=False)}`", f"- Resolved attributes: `{json.dumps(trace['resolved_attributes'], ensure_ascii=False)}`", f"- Resolved/projected relations: `{json.dumps(trace['projected_relations'], ensure_ascii=False)}`", f"- Expected: `{json.dumps(trace['expected'], ensure_ascii=False)}`", ""]
        if trace["root_findings"]:
            for finding in trace["root_findings"]:
                lines += [f"**{finding['finding_id']} — `{finding['classification']}`**", "", finding["root_cause"], "", "Evidence:"]
                lines.extend(f"- {item}" for item in finding["evidence"])
                lines += [""]
        else:
            lines += ["Semantic result: PASS. This case is retained as a historical control. Its provenance check is part of the shared provenance-contract finding below.", ""]
    lines += [
        "## Provenance audit",
        "",
        f"The persisted check is `{provenance['observed_check']}`. This is classified as `{provenance['classification']}` with a contributing `{provenance['contributing_evaluator_condition']}`. The failure is independent of the missing relation findings: relation absence explains relation metrics, but does not by itself explain why the provenance contract fails for 0056 as well.",
        "",
        "Evidence:",
    ]
    lines.extend(f"- {item}" for item in provenance["evidence"])
    lines += [
        "",
        "The contract decision remains a HUMAN GATE: choose whether the authoritative result must carry full-conversation provenance or an explicit segment-scoped provenance field, then align the evaluator and materializer. No automatic repair is authorized from this report.",
        "",
        "## Decision state",
        "",
        "- Resolver freeze: `PRESERVED`",
        "- V6 policy-aligned result: `PASS`",
        "- Holdout result: `FAIL`",
        "- Post-holdout repair: `NOT_AUTHORIZED`",
        "- V7: `BLOCKED`",
        "- Shadow Integration: `BLOCKED`",
        "- Production: `BLOCKED`",
        "",
        "The next decision is whether to authorize a general repair for relation materialization and event/state temporal ownership, with a new unseen validation set. The consumed cases must not be reused as holdouts.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    report = build()
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(_md(report), encoding="utf-8")
    print(json.dumps({"json": str(REPORT_JSON), "markdown": str(REPORT_MD), "holdout_rerun": False}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
