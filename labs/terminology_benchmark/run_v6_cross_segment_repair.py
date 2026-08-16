"""Run the general cross-segment repair against the frozen V6 corpus."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus
from .cross_segment_context import CrossSegmentContextAdapter
from .v6_harness import evaluate_v6


ROOT = Path(__file__).parent
DEFAULT_BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
DEFAULT_DIAGNOSTIC = ROOT / "results" / "context-cross-segment-taxonomy-v6-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-cross-segment-repair-2026-08-15.json"
HOLDOUT_IDS = ("sim-v6-0056", "sim-v6-0057", "sim-v6-0058")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _selected_metrics(report: dict[str, object]) -> dict[str, object]:
    attributes = report["attribute_accuracy"]
    v6 = report["v6_metrics"]
    return {
        "mention_exact_match": attributes["mention_exact_match"],
        "relation_exact_match": attributes["relation_exact_match"],
        "scope_accuracy": attributes["scope_accuracy"],
        "cross_mention_isolation": attributes["cross_mention_isolation"],
        "cross_segment_resolution": v6["cross_segment_resolution"],
        "speaker_attribution": v6["speaker_attribution"],
        "provenance": attributes["provenance"],
        "hard_gate_passed": report["hard_gate_passed"],
    }


def run(*, corpus_path: Path, blind_path: Path, diagnostic_path: Path, output_path: Path) -> dict[str, object]:
    if output_path.exists():
        raise RuntimeError(f"repair result already exists; refusing to overwrite: {output_path}")
    blind = json.loads(blind_path.read_text(encoding="utf-8"))
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != blind.get("official_corpus_sha256"):
        raise RuntimeError("repair corpus does not match frozen blind-run corpus")
    cases = load_corpus(corpus_path)
    if any(case.case_id in HOLDOUT_IDS for case in cases):
        # The official corpus may contain no reserve IDs; this guard also makes
        # accidental holdout execution visible if the input is changed later.
        raise RuntimeError("holdout IDs must not participate in V6 repair")

    repaired_report = asyncio.run(
        evaluate_v6(
            CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases),
            cases,
        )
    )
    baseline_report = blind["report"]
    result = {
        "status": "executed",
        "run_type": "v6-cross-segment-repair",
        "corpus": corpus_path.stem,
        "official_corpus": True,
        "official_corpus_sha256": checksum,
        "blind_baseline_path": str(blind_path),
        "diagnostic_path": str(diagnostic_path),
        "repair_scope": "generalized cross-segment continuity resolver",
        "case_specific_rules": False,
        "canonical_evidence_mutated": False,
        "holdout_ids_excluded": list(HOLDOUT_IDS),
        "shadow_integration": False,
        "production_promotion": False,
        "repair_applied": True,
        "baseline": _selected_metrics(baseline_report),
        "repaired": _selected_metrics(repaired_report),
        "delta": {
            metric: _selected_metrics(repaired_report)[metric] - _selected_metrics(baseline_report)[metric]
            for metric in (
                "mention_exact_match",
                "relation_exact_match",
                "scope_accuracy",
                "cross_mention_isolation",
                "cross_segment_resolution",
                "speaker_attribution",
                "provenance",
            )
        },
        "v6_pass_authorizes_holdout": bool(repaired_report["hard_gate_passed"]),
        "next_action": "holdout-run" if repaired_report["hard_gate_passed"] else "repair-analysis-required",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--blind", type=Path, default=DEFAULT_BLIND)
    parser.add_argument("--diagnostic", type=Path, default=DEFAULT_DIAGNOSTIC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(corpus_path=args.corpus, blind_path=args.blind, diagnostic_path=args.diagnostic, output_path=args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
