"""Report whether the V6 official assembler is allowed to release a corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .corpus import (
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    CONTEXT_VALIDATION_V6_DRAFT_PATH,
    load_corpus,
)
from .v6_corpus import V6AssemblyBlocked, assert_official_v6_ready


ROOT = Path(__file__).parent
SIMULATOR_CANDIDATES = ROOT / "results" / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", type=Path, default=CONTEXT_VALIDATION_V6_DRAFT_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    human_cases = load_corpus(args.draft)
    forbidden = {
        case.text
        for path in (CONTEXT_VALIDATION_V3_PATH, CONTEXT_VALIDATION_V4_PATH, CONTEXT_VALIDATION_V5_PATH)
        for case in load_corpus(path)
    }
    try:
        report = assert_official_v6_ready(human_cases, (), forbidden_texts=forbidden)
        result = {"status": "ready", "report": report}
    except V6AssemblyBlocked as error:
        result = {
            "status": "blocked-pending-human-review",
            "reason": str(error),
            "draft_cases": len(human_cases),
            "simulator_candidates": _candidate_count(SIMULATOR_CANDIDATES),
            "official_corpus_created": False,
        }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def _candidate_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(bool(line.strip()) for line in path.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    main()
