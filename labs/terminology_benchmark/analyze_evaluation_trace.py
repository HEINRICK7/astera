"""CLI for first-divergence analysis of an already-saved evaluation trace."""
from __future__ import annotations

import argparse
import json

from .evaluation_trace import analyze_saved_trace


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", help="path to a ClinicalEvaluationTrace JSON")
    parser.add_argument("--gold", help="optional JSON file containing gold payload")
    args = parser.parse_args()
    gold = None
    if args.gold:
        with open(args.gold, encoding="utf-8") as handle:
            gold = json.load(handle)
    print(json.dumps(analyze_saved_trace(args.trace, gold), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
