"""Generate review-only PT-BR clinical language candidates for future v6."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .corpus import (
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    load_corpus,
)
from .simulator import ClinicalLanguageSimulator, load_failure_seeds, write_candidates


ROOT = Path(__file__).parent
TAXONOMIES = tuple(ROOT / "results" / f"context-taxonomy-v{version}-2026-08-15.json" for version in (3, 4, 5))
CORPORA = (CONTEXT_VALIDATION_V3_PATH, CONTEXT_VALIDATION_V4_PATH, CONTEXT_VALIDATION_V5_PATH)
HISTORICAL_MANIFEST = ROOT / "data" / "historical_failure_manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl",
    )
    parser.add_argument("--per-error-type", type=int, default=1)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    seeds = load_failure_seeds(CORPORA, TAXONOMIES, HISTORICAL_MANIFEST)
    official_cases = tuple(case for path in CORPORA for case in load_corpus(path))
    candidates = ClinicalLanguageSimulator().generate(
        seeds,
        official_cases,
        per_error_type=args.per_error_type,
        limit=args.limit,
    )
    write_candidates(args.output, candidates)
    print(
        json.dumps(
            {
                "status": "candidate-only",
                "provider": "deterministic-clinical-language-simulator",
                "candidate_count": len(candidates),
                "source_corpora": [path.stem for path in CORPORA],
                "official_corpus_mutation": False,
                "output": str(args.output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
