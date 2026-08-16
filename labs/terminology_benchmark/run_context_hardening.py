"""Evaluate PT-BR context hardening with medspaCy plus NIEDE safety rules."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .asset_registry import load_registry
from .context_adapters import (
    DeterministicContextAdapter,
    MedSpaCyContextAdapter,
    OptionalContextProviderUnavailable,
)
from .context_harness import evaluate
from .context_safety import HybridClinicalContextAdapter
from .corpus import CONTEXT_HARDENING_CORPUS_PATH, benchmark_target_terms, load_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Optional authorized spaCy model path/name")
    parser.add_argument("--corpus", type=Path, default=CONTEXT_HARDENING_CORPUS_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = load_corpus(args.corpus)
    is_v5 = args.corpus.stem.endswith("v5")
    composition_thresholds = (
        {
            "relation_exact_match": 0.95,
            "scope_accuracy": 0.97,
            "cross_mention_isolation": 0.95,
        }
        if is_v5
        else None
    )
    result: dict[str, object] = {
        "status": "experimental-only",
        "corpus": args.corpus.stem,
        "cases": len(cases),
        "production_promotion": False,
        "baseline": asyncio.run(
            evaluate(
                DeterministicContextAdapter(),
                cases,
                enforce_composition_gate=is_v5 or args.corpus.stem.endswith("v4"),
                composition_thresholds=composition_thresholds,
            )
        ),
    }
    registry = load_registry()
    decision = registry.authorize("medspacy", "benchmark")
    if not decision.allowed:
        result["hybrid"] = {"status": "blocked", "authorization": decision.to_dict()}
    else:
        try:
            base = MedSpaCyContextAdapter(
                model_name=args.model,
                target_terms=benchmark_target_terms(cases),
            )
            result["medspacy"] = {
                "status": "executed",
                "report": asyncio.run(
                    evaluate(
                        base,
                        cases,
                        enforce_composition_gate=is_v5 or args.corpus.stem.endswith("v4"),
                        composition_thresholds=composition_thresholds,
                    )
                ),
            }
            hybrid = HybridClinicalContextAdapter(base)
            result["hybrid"] = {
                "status": "executed",
                "report": asyncio.run(
                    evaluate(
                        hybrid,
                        cases,
                        enforce_composition_gate=is_v5 or args.corpus.stem.endswith("v4"),
                        composition_thresholds=composition_thresholds,
                    )
                ),
            }
        except OptionalContextProviderUnavailable as error:
            result["medspacy"] = {"status": "unavailable", "reason": str(error)}
            result["hybrid"] = {"status": "unavailable", "reason": str(error)}
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
