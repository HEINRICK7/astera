"""Generate V6 error taxonomy from the recorded first blind-run adapter."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path

from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus
from .error_taxonomy import analyze


ROOT = Path(__file__).parent
DEFAULT_BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-taxonomy-v6-blind-2026-08-15.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*, corpus_path: Path, blind_path: Path, output_path: Path) -> dict[str, object]:
    blind = json.loads(blind_path.read_text(encoding="utf-8"))
    if blind.get("run_type") != "first-blind-run" or blind.get("run_count") != 1:
        raise RuntimeError("taxonomy requires the recorded first blind run")
    corpus_checksum = _sha256(corpus_path)
    if corpus_checksum != blind.get("official_corpus_sha256"):
        raise RuntimeError("taxonomy corpus checksum does not match the blind run")
    cases = load_corpus(corpus_path)
    result = {
        "status": "executed",
        "run_type": "post-blind-error-taxonomy",
        "corpus": corpus_path.stem,
        "official_corpus": True,
        "official_corpus_sha256": corpus_checksum,
        "blind_run_path": str(blind_path),
        "repair_applied": False,
        "provider": "niede-pt-br-safety-rules",
        "report": asyncio.run(analyze(NieDEPtBrSafetyRules(), cases)),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--blind", type=Path, default=DEFAULT_BLIND)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(corpus_path=args.corpus, blind_path=args.blind, output_path=args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
