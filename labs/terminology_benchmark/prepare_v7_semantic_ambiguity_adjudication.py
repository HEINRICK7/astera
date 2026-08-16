"""Prepare the five-cluster V7 semantic adjudication sheet.

Reads existing AI-assisted proposals only. It does not re-adjudicate cases,
change gold, or execute any semantic component.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
PROPOSAL_DIR = ROOT / "results/v7-ai-assisted-adjudication-2026-08-15"
OUTPUT_JSON = PROPOSAL_DIR / "V7_SEMANTIC_AMBIGUITY_ADJUDICATION.json"
OUTPUT_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_SEMANTIC_AMBIGUITY_ADJUDICATION.md"
CLUSTERS = {
    "AMB-FREQ-001": {
        "label": "frequency",
        "policy_status": "POLICY_EXTENSION_REQUIRED",
        "policy": ["SEM-FREQ-001"],
        "problem": "A transition says that the schedule changed, but the text repeats the same frequency value as both old and current and supplies no distinct new value.",
        "interpretation_a": "Treat the explicit repeated value as the current frequency and do not materialize a transition relation.",
        "interpretation_b": "Treat the transition as unresolved because the current frequency cannot be distinguished from the historical value.",
        "gap": "SEM-FREQ-001 defines current ownership when OLD_STATE and NEW_STATE are explicit, but not a contradictory or under-specified transition.",
        "recommendation": "Prefer B for gold: preserve the explicit surface evidence, but do not invent CHANGED_FROM or a hidden new schedule. Consider SEM-FREQ-002 only if the human decision wants a formal unresolved-transition rule.",
    },
    "AMB-TEMP-001": {
        "label": "temporality",
        "policy_status": "POLICY_ALREADY_DEFINES",
        "policy": ["SEM-TEMP-001", "SEM-XSEG-001"],
        "problem": "A past symptom/event is followed by a generic current phrase such as ‘a queixa em joelho esquerdo’, which does not name a unique clinical concept.",
        "interpretation_a": "Transfer the previous symptom concept to the current generic phrase and assign current temporality plus the new location.",
        "interpretation_b": "Keep the named historical event past; leave the generic current phrase unresolved rather than transferring concept or temporality.",
        "gap": "The existing rules already require a unique compatible antecedent and prohibit forced cross-segment inheritance; the remaining choice is gold representation for a non-entity surface.",
        "recommendation": "Prefer B: no concept transfer, no temporal ownership transfer, and unresolved/omitted generic mention. No new policy is required.",
    },
    "AMB-CORR-001": {
        "label": "correction/revision",
        "policy_status": "POLICY_EXTENSION_REQUIRED",
        "policy": ["SEM-NEG-001", "SEM-XSEG-001"],
        "problem": "A clinician/patient correction explicitly rejects the first clinical term and leaves only a location as the corrected content.",
        "interpretation_a": "Retain the first clinical mention as historical evidence and add the corrected location as a separate mention.",
        "interpretation_b": "Treat the first mention as superseded and do not create a clinical entity from the location alone.",
        "gap": "Current policy scopes negation and ownership but does not define supersession semantics for a correction that removes the clinical concept.",
        "recommendation": "Prefer B for these cases. Consider SEM-CORR-001: explicit correction supersedes the rejected entity; location-only residue is not a clinical mention unless independently named.",
    },
    "AMB-SELF-001": {
        "label": "self-reference/self-correction",
        "policy_status": "POLICY_EXTENSION_REQUIRED",
        "policy": ["SEM-DOSE-001", "SEM-XSEG-001"],
        "problem": "The patient first states one dose and then says, ‘pensando melhor’, that another value was correct; the text does not establish whether the first value was ever a true historical state.",
        "interpretation_a": "Use the later value as current and retain the earlier value with CHANGED_FROM.",
        "interpretation_b": "Use the later value as current but treat the earlier value as superseded speech, without CHANGED_FROM unless a real transition is explicitly asserted.",
        "gap": "SEM-DOSE-001 covers explicit old-to-new transitions but not epistemic correction of a previously misstated value.",
        "recommendation": "Prefer B: later self-correction owns the current value; do not encode a historical dose transition from a statement explicitly corrected as mistaken. Consider SEM-SELF-001.",
    },
    "AMB-SPEAKER-001": {
        "label": "speaker attribution/experiencer",
        "policy_status": "POLICY_ALREADY_DEFINES",
        "policy": ["SEM-EXP-001", "SEM-XSEG-001"],
        "problem": "A prior speaker is mentioned, the patient confirms only a location, and says that another part belonged to a relative; the clinical entity associated with the relative is not uniquely identified.",
        "interpretation_a": "Assign the prior symptom/event to the relative and keep the patient’s later medication and negation separate.",
        "interpretation_b": "Do not assign an experiencer to the ambiguous prior clinical content; retain only the explicitly grounded patient mentions.",
        "gap": "The existing rules already require a unique compatible owner and prohibit experiencer leakage; the open question is whether an indirect family reference is enough to ground an entity.",
        "recommendation": "Prefer B: unresolved ownership for the ungrounded prior clinical content. No new policy is required; apply SEM-EXP-001 and SEM-XSEG-001 conservatively.",
    },
}


def _load_reviews() -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    for path in sorted(PROPOSAL_DIR.glob("v7-batch-0[5-8]-ai-proposal.json")):
        reviews.extend(json.loads(path.read_text(encoding="utf-8")).get("reviews", []))
    return reviews


def main() -> None:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for review in _load_reviews():
        cluster = review.get("ambiguity_cluster")
        if cluster in CLUSTERS:
            grouped[cluster].append(review)
    if any(len(grouped[cluster]) != 10 for cluster in CLUSTERS):
        raise RuntimeError({cluster: len(grouped[cluster]) for cluster in CLUSTERS})

    entries = []
    for cluster, spec in CLUSTERS.items():
        examples = []
        for review in grouped[cluster][:3]:
            examples.append({
                "case_id": review["candidate_id"],
                "scenario_family": review["scenario_family"],
                "text": review["text"],
                "segments": review["segments"],
                "existing_ai_note": review.get("review_notes"),
            })
        entries.append({"cluster": cluster, "case_count": 10, **spec, "examples": examples})

    report = {
        "status": "HUMAN_GATE_SEMANTIC_ADJUDICATION",
        "scope": "existing_ai_assisted_proposals_batches_05_08",
        "policy_version": "1.2",
        "cluster_count": len(entries),
        "ambiguous_case_count": sum(entry["case_count"] for entry in entries),
        "clusters": entries,
        "reprocessed_cases": False,
        "approved_proposals_changed": False,
        "gold_changed": False,
        "policy_changed": False,
        "resolver_executed": False,
        "composition_authorized": False,
        "corpus_freeze_complete": False,
        "blind_run": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
        "next_gate": "human_decide_the_five_cluster_policies_before_composition_or_freeze",
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# V7 Semantic Ambiguity Adjudication",
        "",
        "Status: **HUMAN GATE — STOP**",
        "",
        "This sheet summarizes the existing 50 ambiguous proposals into five human semantic decisions. No cases were reprocessed and no gold, policy, resolver, or corpus was changed.",
        "",
    ]
    for entry in entries:
        lines.extend([
            f"## {entry['cluster']} — {entry['label']}",
            "",
            f"Cases: **{entry['case_count']}**",
            f"Classification: `{entry['policy_status']}`",
            f"Current policy: {', '.join(f'`{p}`' for p in entry['policy'])}",
            "",
            f"Problem: {entry['problem']}",
            "",
            f"- Interpretation A: {entry['interpretation_a']}",
            f"- Interpretation B: {entry['interpretation_b']}",
            f"- Policy gap: {entry['gap']}",
            f"- Agent recommendation: {entry['recommendation']}",
            "",
            "### Representative examples",
            "",
        ])
        for example in entry["examples"]:
            lines.extend([f"#### `{example['case_id']}`", "", "```text", example["text"], "```", ""])
    lines.extend([
        "## Hard stops",
        "",
        "- composition: NOT AUTHORIZED",
        "- V7 freeze: NOT AUTHORIZED",
        "- resolver execution: FALSE",
        "- blind run: BLOCKED",
        "- Shadow Integration: BLOCKED",
        "- Production: BLOCKED",
    ])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "clusters": [{"cluster": e["cluster"], "cases": e["case_count"], "classification": e["policy_status"]} for e in entries], "output": str(OUTPUT_MD)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
