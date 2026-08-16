"""Consolidate AI-assisted V7 proposals without composing or freezing V7."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
PROPOSAL_DIR = RESULTS / "v7-ai-assisted-adjudication-2026-08-15"
OUTPUT = PROPOSAL_DIR / "V7_AI_ASSISTED_ADJUDICATION_FINAL_REPORT.json"
OUTPUT_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_AI_ASSISTED_ADJUDICATION_FINAL_REPORT.md"
ALLOWED_POLICIES = {"SEM-STATUS-001", "SEM-TEMP-001", "SEM-NEG-001", "SEM-EXP-001", "SEM-DOSE-001", "SEM-FREQ-001", "SEM-XSEG-001"}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized_shape(gold: list[dict[str, Any]]) -> tuple[Any, ...]:
    shape = []
    for item in gold:
        concept_prefix = str(item.get("concept_id", "")).split(".", 1)[0]
        fields = tuple(sorted(key for key in item if key not in {
            "surface", "concept_id", "segment_ids", "attribute_provenance", "relation_provenance", "relations",
            "dose", "dose_value", "dose_unit", "frequency", "laterality",
        }))
        # Laterality is conditional on the lexical location: "abdome" and
        # "joelho esquerdo" must share the same semantic template even though
        # only the latter authorizes HAS_LATERALITY.
        relation_types = tuple(sorted(
            relation.get("relation_type")
            for relation in item.get("relations", [])
            if relation.get("relation_type") != "HAS_LATERALITY"
        ))
        shape.append((concept_prefix, fields, relation_types))
    return tuple(shape)


def main() -> None:
    validation_paths = sorted(PROPOSAL_DIR.glob("v7-batch-0[5-8]-validation.json"))
    proposal_paths = sorted(PROPOSAL_DIR.glob("v7-batch-0[5-8]-ai-proposal.json"))
    if len(validation_paths) != 4 or len(proposal_paths) != 4:
        raise RuntimeError("expected exactly four validated proposal batches (05-08)")

    reviews: list[dict[str, Any]] = []
    batch_results = []
    schema_blockers: list[str] = []
    for validation_path, proposal_path in zip(validation_paths, proposal_paths):
        validation = _json(validation_path)
        if not validation.get("structural_validation_passed"):
            schema_blockers.extend(validation.get("structural_errors", []))
        payload = _json(proposal_path)
        batch_reviews = payload.get("reviews", [])
        reviews.extend(batch_reviews)
        batch_results.append({
            "batch_id": payload.get("batch_id"),
            "case_range": payload.get("case_range"),
            "decision_counts": payload.get("decision_counts"),
            "structural_validation": "PASS" if validation.get("structural_validation_passed") else "FAIL",
            "mentions": validation.get("mentions"),
            "relations": validation.get("relations"),
            "provenance_valid": validation.get("provenance_valid"),
            "output": str(proposal_path),
        })

    counts = Counter(item.get("decision") for item in reviews)
    approved = [item for item in reviews if item.get("decision") == "APPROVED"]
    ambiguous = [item for item in reviews if item.get("decision") == "AMBIGUOUS"]
    pending = [item for item in reviews if item.get("decision") == "PENDING_HUMAN"]
    mentions = sum(len(item.get("gold", [])) for item in approved)
    relations = sum(sum(len(mention.get("relations", [])) for mention in item.get("gold", [])) for item in approved)
    provenance_valid = sum(1 for item in approved if item.get("gold"))

    cluster_cases: defaultdict[str, list[str]] = defaultdict(list)
    for item in ambiguous:
        cluster_cases[str(item.get("ambiguity_cluster"))].append(item["candidate_id"])
    ambiguity_clusters = {
        cluster: {"count": len(case_ids), "case_ids": case_ids}
        for cluster, case_ids in sorted(cluster_cases.items())
    }

    family_decisions: defaultdict[str, set[str]] = defaultdict(set)
    family_shapes: defaultdict[str, set[tuple[Any, ...]]] = defaultdict(set)
    policy_conflicts: list[str] = []
    for item in reviews:
        family = item.get("scenario_family", "UNKNOWN")
        decision = item.get("decision")
        family_decisions[family].add(str(decision))
        if decision == "APPROVED":
            family_shapes[family].add(_normalized_shape(item.get("gold", [])))
        for policy_id in item.get("policy_ids", []):
            if policy_id not in ALLOWED_POLICIES:
                policy_conflicts.append(f"{item.get('candidate_id')}: unknown policy {policy_id}")
        if item.get("policy_version") != "clinical-semantic-policy-v1.2":
            policy_conflicts.append(f"{item.get('candidate_id')}: policy version mismatch")

    consistency_conflicts = []
    for family, decisions in sorted(family_decisions.items()):
        if len(decisions) > 1:
            consistency_conflicts.append(f"{family}: mixed decisions {sorted(decisions)}")
        if len(family_shapes.get(family, set())) > 1:
            consistency_conflicts.append(f"{family}: approved gold shape diverges")

    report = {
        "status": "HUMAN_GATE_FINAL_ADJUDICATION",
        "scope": "BATCHES_05_08_ONLY",
        "policy_version": "1.2",
        "case_count": len(reviews),
        "decision_counts": {key: counts.get(key, 0) for key in ("APPROVED", "REJECTED", "AMBIGUOUS", "PENDING_HUMAN")},
        "mentions": mentions,
        "relations": relations,
        "provenance_valid_approved_cases": provenance_valid,
        "batch_results": batch_results,
        "ambiguity_clusters": ambiguity_clusters,
        "cross_batch_consistency": {
            "status": "PASS" if not consistency_conflicts else "FAIL",
            "family_decisions": {family: sorted(values) for family, values in sorted(family_decisions.items())},
            "conflicts": consistency_conflicts,
        },
        "policy_conflicts": sorted(set(policy_conflicts)),
        "schema_blockers": schema_blockers,
        "proposed_composition": {
            "include_ai_proposals": [item["candidate_id"] for item in approved],
            "exclude_as_ambiguous": [item["candidate_id"] for item in ambiguous],
            "rejected": [item["candidate_id"] for item in reviews if item.get("decision") == "REJECTED"],
            "requires_human_confirmation": True,
            "official_gold_created": False,
        },
        "resolver_executed": False,
        "official_v7_run": False,
        "corpus_freeze_complete": False,
        "blind_run": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
        "next_action": "HUMAN_GATE_REVIEW_AMBIGUITY_CLUSTERS_AND_AUTHORIZE_COMPOSITION_ONLY",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# NIEDE V7 — AI-Assisted Gold Adjudication Final Report",
        "",
        "Status: **HUMAN GATE — STOP**",
        "",
        "Scope: batches 05–08 only. These are non-official AI-assisted proposals; no V7 gold was composed or frozen.",
        "",
        f"- Policy: `v{report['policy_version']}`",
        f"- Cases: `{report['case_count']}`",
        f"- APPROVED proposals: `{report['decision_counts']['APPROVED']}`",
        f"- AMBIGUOUS: `{report['decision_counts']['AMBIGUOUS']}`",
        f"- REJECTED: `{report['decision_counts']['REJECTED']}`",
        f"- PENDING_HUMAN in proposal scope: `{report['decision_counts']['PENDING_HUMAN']}`",
        f"- Structural validation: `{'PASS' if not schema_blockers else 'FAIL'}`",
        f"- Cross-batch consistency: `{report['cross_batch_consistency']['status']}`",
        f"- Policy conflicts: `{len(report['policy_conflicts'])}`",
        "",
        "## Ambiguity clusters",
        "",
    ]
    for cluster, data in ambiguity_clusters.items():
        lines.append(f"- `{cluster}`: {data['count']} cases")
    lines.extend([
        "",
        "## Proposed composition",
        "",
        "Approved proposals may be considered for composition only after human confirmation. Ambiguous cases remain excluded until a policy decision exists.",
        "",
        "## Hard stops",
        "",
        "- official V7 corpus: NOT CREATED",
        "- corpus freeze: NOT AUTHORIZED",
        "- resolver execution: FALSE",
        "- blind run: BLOCKED",
        "- Shadow Integration: BLOCKED",
        "- Production: BLOCKED",
    ])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "scope": report["scope"], "decision_counts": report["decision_counts"], "ambiguity_clusters": {key: value["count"] for key, value in ambiguity_clusters.items()}, "consistency": report["cross_batch_consistency"], "policy_conflicts": len(report["policy_conflicts"]), "schema_blockers": len(schema_blockers), "output": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
