"""Analyze preserved V7 blind aggregates without rerunning the resolver."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
OFFICIAL = DATA / "v7_unseen_generalization_official.jsonl"
BLIND = RESULTS / "v7-blind-run-2026-08-15.json"
TAXONOMY = RESULTS / "V7_BLIND_ERROR_TAXONOMY.md"
OUT_JSON = RESULTS / "V7_ROOT_CAUSE_MATRIX.json"
OUT_DECOMP = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_BLIND_FAILURE_DECOMPOSITION.md"
OUT_GAP = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_CAPABILITY_GAP_REPORT.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_official() -> list[dict[str, Any]]:
    return [json.loads(line) for line in OFFICIAL.read_text(encoding="utf-8").splitlines() if line.strip()]


def _family(record: dict[str, Any]) -> str:
    return record.get("scenario_family", "UNKNOWN")


def main() -> None:
    blind = json.loads(BLIND.read_text(encoding="utf-8"))
    evaluation = blind["evaluation"]
    records = _load_official()
    family_gold: defaultdict[str, dict[str, int]] = defaultdict(lambda: Counter())
    for record in records:
        family = _family(record)
        family_gold[family]["cases"] += 1
        for mention in record.get("gold", []):
            family_gold[family]["mentions"] += 1
            family_gold[family]["cross_segment_mentions"] += int(len(mention.get("segment_ids", [])) > 1)

    family_metrics = {}
    for family, counts in sorted(family_gold.items()):
        observed = evaluation["group_metrics"].get(f"family:{family}", {})
        family_metrics[family] = {
            "case_count": counts["cases"],
            "mention_count": counts["mentions"],
            "mention_exact": observed.get("mention_exact_match"),
            "relation_exact": observed.get("relation_exact_match"),
            "cross_segment_gold_mentions": counts["cross_segment_mentions"],
            "cross_segment_resolution": "NOT_AVAILABLE_PER_FAMILY_IN_PRESERVED_TRACE",
            "primary_root_cause": "UNDETERMINED_WITHOUT_CASE_TRACE",
            "secondary_root_cause": "UNDETERMINED_WITHOUT_CASE_TRACE",
        }
    top_failing_families = sorted(
        ((family, metrics.get("mention_exact")) for family, metrics in family_metrics.items()),
        key=lambda pair: (pair[1] if pair[1] is not None else 1.0, pair[0]),
    )[:5]

    field_taxonomy = evaluation.get("failure_taxonomy", {})
    top_observed = sorted(field_taxonomy.items(), key=lambda pair: (-pair[1], pair[0]))
    root_cause_matrix = {
        "status": "HUMAN_GATE_DIAGNOSTIC_INCOMPLETE",
        "blind_execution_id": blind["execution_id"],
        "blind_status": blind["status"],
        "official_corpus_checksum": blind["corpus_checksum"],
        "resolver_config_checksum": blind["resolver_config_checksum"],
        "policy_version": blind["policy_version"],
        "rerun_performed": False,
        "case_level_predictions_preserved": False,
        "case_level_traces_preserved": False,
        "case_level_classification": "NOT_DETERMINABLE",
        "observability_gap": {
            "root_cause": "MISSING_PER_CASE_PREDICTION_TRACE",
            "impact": "first_divergence_stage and causal G1-G4 classification cannot be proven per case",
            "required_artifact": "immutable per-case prediction/trace record from a future authorized run",
        },
        "confirmed_repair_class_counts": {"G1": 0, "G2": 0, "G3": 0, "G4": 0},
        "undetermined_repair_class_counts": {"G1": "NOT_DETERMINABLE", "G2": "NOT_DETERMINABLE", "G3": "NOT_DETERMINABLE", "G4": "NOT_DETERMINABLE"},
        "capability_gap": "NOT_PROVEN",
        "g4_evidence": False,
        "observed_field_mismatch_counts": field_taxonomy,
        "top_observed_mismatch_dimensions": top_observed,
        "family_matrix": family_metrics,
        "top_failing_families": top_failing_families,
        "aggregate_metrics": evaluation["metrics"],
        "group_metrics_preserved": evaluation["group_metrics"],
        "recommended_next_milestone": "V7 Blind Traceability & Causal Attribution Contract",
    }
    OUT_JSON.write_text(json.dumps(root_cause_matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    decomp = [
        "# V7 Blind Failure Decomposition",
        "",
        "Status: **HUMAN GATE — DIAGNOSTIC LIMITATION**",
        "",
        "The single V7 Blind Run was not rerun. The preserved artifact contains aggregate metrics, family/entity/scope groups, and field mismatch counts, but no per-case predictions or traces.",
        "Therefore `case_id`, `expected → predicted`, `first_divergence_stage`, and causal G1–G4 classification cannot be asserted without inventing evidence.",
        "",
        "## Observed aggregate evidence",
        "",
    ]
    for key, value in evaluation["metrics"].items():
        decomp.append(f"- `{key}`: `{value:.6f}`")
    decomp.extend([
        "",
        "## Observed mismatch dimensions (not causal root causes)",
        "",
    ])
    for key, value in top_observed:
        decomp.append(f"- `{key}`: `{value}`")
    decomp.extend([
        "",
        "## Causal classification status",
        "",
        "- Confirmed G1: `0`",
        "- Confirmed G2: `0`",
        "- Confirmed G3: `0`",
        "- Confirmed G4: `0`",
        "- All per-case G1–G4 assignments: `NOT_DETERMINABLE`",
        "- G4/LLM evidence: `NOT PROVEN`",
        "",
        "## Top failing scenario families (observed mention exact)",
        "",
    ])
    for family, score in top_failing_families:
        decomp.append(f"- `{family}`: `{score:.6f}`")
    decomp.extend([
        "",
        "## First divergence",
        "",
        "Not observable in the preserved Blind Run artifact. The aggregate pattern supports an architectural hypothesis around cross-turn reference/state/ownership, but does not prove whether the first divergence is mention detection, antecedent resolution, ownership, or relation generation.",
        "",
        "## Required next milestone",
        "",
        "Add an immutable per-case prediction and semantic trace contract to a future authorized evaluation path. The trace must preserve candidate, resolved, projected, evaluated, expected, first divergence stage, and downstream effects. This is an observability/causal-attribution milestone, not Repair V8.",
        "",
        "Hard stops: no repair, no V7 rerun, no gold/corpus change, Shadow blocked, Production blocked.",
    ])
    OUT_DECOMP.write_text("\n".join(decomp) + "\n", encoding="utf-8")

    gap = [
        "# V7 Capability Gap Report",
        "",
        "Status: **HUMAN GATE**",
        "",
        "## Evidence",
        "",
        f"- Blind execution: `{blind['execution_id']}`",
        f"- mention exact: `{evaluation['metrics']['mention_exact_match']:.6f}`",
        f"- relation exact: `{evaluation['metrics']['relation_exact_match']:.6f}`",
        f"- cross-segment resolution: `{evaluation['metrics']['cross_segment_resolution']:.6f}`",
        f"- provenance: `{evaluation['metrics']['provenance']:.6f}`",
        "",
        "## Interpretation",
        "",
        "The evidence is consistent with a gap in conversational composition, reference continuity, and attribute ownership. It does not prove a new capability boundary or justify an LLM/provider decision, because predictions were not preserved per case.",
        "",
        "Supported architectural hypotheses:",
        "",
        "- an explicit Clinical Conversation State may be needed for active entities and referents;",
        "- topic stack and speaker/experiencer state may need first-class representation;",
        "- correction/supersession and temporal event state may need explicit graph structure;",
        "- relation errors may be downstream effects of upstream identity/ownership failures.",
        "",
        "These remain hypotheses until a traceable evaluation can identify the first divergence.",
        "",
        "## Capability classification",
        "",
        "- G1 local bug: not proven",
        "- G2 architectural limitation: plausible, not proven per case",
        "- G3 missing capability: not proven",
        "- G4 probabilistic/LLM requirement: no evidence sufficient to recommend",
        "",
        "Recommended next milestone: **V7 Blind Traceability & Causal Attribution Contract**, followed by a HUMAN GATE before any repair or new evaluation.",
        "",
        "No repair, rerun, provider, policy, gold, or corpus change is authorized.",
    ]
    OUT_GAP.write_text("\n".join(gap) + "\n", encoding="utf-8")
    print(json.dumps({"status": root_cause_matrix["status"], "case_level_trace_available": False, "g1_confirmed": 0, "g2_confirmed": 0, "g3_confirmed": 0, "g4_confirmed": 0, "capability_gap": "NOT_PROVEN", "top_observed_mismatches": top_observed[:10], "outputs": [str(OUT_DECOMP), str(OUT_JSON), str(OUT_GAP)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
