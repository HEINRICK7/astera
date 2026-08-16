"""Run the first frozen-code validation against the V6 draft only."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_DRAFT_PATH, load_corpus
from .v6_harness import evaluate_v6
from .v6_corpus import validate_v6_draft


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_DRAFT_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = load_corpus(args.corpus)
    result = {
        "status": "draft-only",
        "corpus": args.corpus.stem,
        "official_corpus": False,
        "production_promotion": False,
        "draft_validation": validate_v6_draft(cases),
        "report": asyncio.run(evaluate_v6(NieDEPtBrSafetyRules(), cases)),
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
