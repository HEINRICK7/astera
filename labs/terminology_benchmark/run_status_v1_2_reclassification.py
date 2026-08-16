"""Reclassify V6 status findings against approved SEM-STATUS-001 v1.2."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DOCS = ROOT.parent.parent / "docs" / "clinical-conversational-semantics"
QUEUE = DOCS / "STATUS_EXPLICIT_CUE_ANALYSIS.json"
POLICY = "SEM-STATUS-001"
VERSION = "1.2"


def _reclassify(record: dict[str, Any]) -> dict[str, Any]:
    entity_type = record["entity_type"]
    classification = record["classification"]
    gold_status = record["gold_status"]
    resolved_status = record["resolved_status"]

    # The approved v1.2 default applies to all findings in this queue. No
    # explicit lifecycle or medication lifecycle finding is present, but keep
    # the branches explicit so a future queue cannot silently be misread.
    if classification in {"EXPLICIT_LIFECYCLE_STATUS", "MEDICATION_LIFECYCLE"}:
        normative_status = "human_adjudication_required"
        classification_result = "TYPE_C_POLICY_UNDEFINED"
        reason = "explicit lifecycle vocabulary/ownership requires a separate approved rule"
    else:
        normative_status = None
        if gold_status == normative_status and resolved_status != normative_status:
            classification_result = "TYPE_A_RESOLVER_ERROR"
            reason = "resolver materialized status although v1.2 requires null without explicit lifecycle evidence"
        elif gold_status != normative_status and resolved_status == normative_status:
            classification_result = "TYPE_B_GOLD_ISSUE"
            reason = "gold retains status although v1.2 defines this assertion/temporal expression as status null"
        elif gold_status == normative_status and resolved_status == normative_status:
            classification_result = "ALIGNED"
            reason = "gold and resolved status both satisfy v1.2"
        else:
            classification_result = "TYPE_C_POLICY_UNDEFINED"
            reason = "gold and resolved status differ from the v1.2 default in a way requiring policy adjudication"

    return {
        "case_id": record["case_id"],
        "surface": record["surface"],
        "entity_type": entity_type,
        "text": record["text"],
        "gold_status": gold_status,
        "resolved_status": resolved_status,
        "normative_status_v1_2": normative_status,
        "status_failure_scope": record["status_failure_scope"],
        "source_classification": classification,
        "classification": classification_result,
        "reason": reason,
        "explicit_status_cue": record["explicit_status_cue"],
        "temporal_cues": record["temporal_cues"],
        "negation": record["negation"],
        "type_b_fields_ignored": record["type_b_fields_ignored"],
    }


def render(report: dict[str, Any]) -> str:
    lines = [
        "# SEM-STATUS-001 v1.2 — V6 Status Reclassification",
        "",
        "Status: **HUMAN GATE — REPAIR V6 NOT AUTHORIZED**  ",
        f"Policy: `{POLICY}`  ",
        f"Version: `{VERSION}`  ",
        "Decision: **APPROVED — documentation only**  ",
        f"V6 checksum: `{report['frozen_v6_checksum']}`",
        "",
        "## Scope",
        "",
        "The 90 status findings were reclassified against the approved v1.2 "
        "normative default. This does not alter resolver output, gold, corpus, "
        "or benchmark history.",
        "",
        "## Result",
        "",
        f"- status findings: **{report['status_findings']}**",
        f"- status-only failures: **{report['status_only_failures']}**",
        f"- normative null: **{report['normative_null']}**",
        f"- explicit lifecycle: **{report['explicit_lifecycle']}**",
        f"- medication lifecycle: **{report['medication_lifecycle']}**",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for key, value in report["classification_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Status transitions",
        "",
        "| Gold → resolved | Reclassified result | Count |",
        "|---|---|---:|",
    ]
    for item in report["transition_counts"]:
        lines.append(f"| {item['transition']} | {item['classification']} | {item['count']} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- `None → present` and `None → historical` are resolver errors under v1.2 "
        "when no explicit lifecycle cue exists.",
        "- `present → None` is a gold inconsistency under v1.2 for these nine "
        "assertion-only cases; gold remains untouched and review-only.",
        "- `sim-v6-0040` remains a status Type B finding here, while its separate "
        "negation mismatch remains visible in the source audit.",
        "",
        "## Invariants",
        "",
        "- policy_changes: **documentation only**",
        "- resolver_changes: **0**",
        "- gold_changes: **0**",
        "- corpus_changes: **0**",
        "- checksum: **preserved**",
        "- Repair V6: **NOT AUTHORIZED**",
        "- holdouts: **NOT_EXECUTED**",
        "- V7 / Shadow / Production: **BLOCKED**",
        "",
        "The complete item-level queue is in `STATUS_V1_2_RECLASSIFICATION.json`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    source = json.loads(QUEUE.read_text(encoding="utf-8"))
    records = [_reclassify(record) for record in source["records"]]
    counts: Counter[str] = Counter(record["classification"] for record in records)
    transitions: Counter[tuple[str, str]] = Counter(
        (
            f"{record['gold_status']} → {record['resolved_status']}",
            record["classification"],
        )
        for record in records
    )
    transition_counts = [
        {"transition": transition, "classification": classification, "count": count}
        for (transition, classification), count in sorted(transitions.items())
    ]
    report = {
        "status": "HUMAN_GATE_REQUIRED",
        "policy": POLICY,
        "version": VERSION,
        "decision": "APPROVE_DOCUMENTATION_ONLY",
        "frozen_v6_checksum": source["frozen_corpus_sha256"],
        "status_findings": len(records),
        "status_only_failures": sum(record["status_failure_scope"] == "only_status" for record in records),
        "normative_null": sum(record["normative_status_v1_2"] is None for record in records),
        "explicit_lifecycle": sum(
            record["source_classification"] == "EXPLICIT_LIFECYCLE_STATUS" for record in records
        ),
        "medication_lifecycle": sum(
            record["source_classification"] == "MEDICATION_LIFECYCLE" for record in records
        ),
        "classification_counts": {
            key: counts[key]
            for key in (
                "TYPE_A_RESOLVER_ERROR",
                "TYPE_B_GOLD_ISSUE",
                "TYPE_C_POLICY_UNDEFINED",
                "ALIGNED",
            )
        },
        "transition_counts": transition_counts,
        "mutations": {
            "policy_changes": "documentation_only",
            "resolver_changes": 0,
            "gold_changes": 0,
            "corpus_changes": 0,
            "repair_started": False,
        },
        "records": records,
    }
    (DOCS / "STATUS_V1_2_RECLASSIFICATION.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (DOCS / "STATUS_V1_2_RECLASSIFICATION.md").write_text(render(report), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "records"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
