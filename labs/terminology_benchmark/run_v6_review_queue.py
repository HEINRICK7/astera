"""Display the V6 candidate review queue without approving candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .review_queue import build_review_packet, format_review_packet, load_candidate_records, write_review_template


ROOT = Path(__file__).parent
DEFAULT_CANDIDATES = ROOT / "results" / "clinical-language-simulator-v6-candidates-2026-08-15.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Render a review packet; neither format approves or writes official gold.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write an editable review worksheet outside the official corpus.",
    )
    args = parser.parse_args()

    packet = build_review_packet(load_candidate_records(args.input))
    if args.output:
        write_review_template(args.output, packet)
    if args.format == "json":
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print(format_review_packet(packet))
    print(
        json.dumps(
            {
                "status": "review-only",
                "candidate_count": len(packet),
                "approved": 0,
                "official_corpus_mutation": False,
                "review_template": str(args.output) if args.output else None,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
