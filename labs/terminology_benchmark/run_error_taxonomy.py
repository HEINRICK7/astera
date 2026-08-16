"""Generate the v3 error taxonomy without changing the corpus."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .asset_registry import load_registry
from .context_adapters import MedSpaCyContextAdapter
from .context_safety import HybridClinicalContextAdapter
from .corpus import CONTEXT_VALIDATION_V3_PATH, benchmark_target_terms, load_corpus
from .error_taxonomy import analyze


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V3_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = load_corpus(args.corpus)
    decision = load_registry().authorize("medspacy", "benchmark")
    if not decision.allowed:
        result = {"status": "blocked", "authorization": decision.to_dict()}
    else:
        adapter = MedSpaCyContextAdapter(target_terms=benchmark_target_terms(cases))
        result = {
            "status": "executed",
            "corpus": args.corpus.stem,
            "report": asyncio.run(analyze(HybridClinicalContextAdapter(adapter), cases)),
        }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
