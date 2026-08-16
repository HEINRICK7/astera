#!/usr/bin/env python3
"""Run reproducible HTTP batch measurements against the real NIM endpoint."""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, type=Path)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--runs", default=3, type=int)
    parser.add_argument("--language", default=os.getenv("PARAKEET_LANGUAGE", "en-US"))
    parser.add_argument("--model", default=os.getenv("PARAKEET_MODEL") or None)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def main() -> int:
    args = parse_args()
    if args.runs < 1:
        raise SystemExit("--runs deve ser >= 1")
    if not args.audio.is_file():
        raise SystemExit(f"Áudio não encontrado: {args.audio}")
    if args.reference and not args.reference.is_file():
        raise SystemExit(f"Referência não encontrada: {args.reference}")

    script = Path(__file__).with_name("batch_probe.py")
    runs: list[dict[str, Any]] = []
    for index in range(args.runs):
        command = [sys.executable, str(script), "--audio", str(args.audio), "--language", args.language]
        if args.model:
            command.extend(["--model", args.model])
        started = time.perf_counter()
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        elapsed = time.perf_counter() - started
        payload: Any = json.loads(completed.stdout) if completed.stdout else None
        runs.append({"run": index + 1, "wall_seconds": round(elapsed, 6), "result": payload, "stderr": completed.stderr})

    texts = [
        item["result"]["response"].get("text", "")
        for item in runs
        if item["result"] and item["result"].get("response")
    ]
    wer: float | None = None
    cer: float | None = None
    if args.reference and texts:
        from jiwer import cer, wer as jiwer_wer

        reference = normalize(args.reference.read_text(encoding="utf-8"))
        wer = jiwer_wer(reference, normalize(texts[-1]))
        cer = cer(reference, normalize(texts[-1]))

    durations = [item["wall_seconds"] for item in runs]
    report = {
        "protocol": "http-batch",
        "provider": "nvidia-speech-nim",
        "audio": args.audio.name,
        "language": args.language,
        "model": args.model,
        "runs": runs,
        "metrics": {
            "wer": wer,
            "cer": cer,
            "latency_seconds_mean": statistics.mean(durations),
            "latency_seconds_min": min(durations),
            "latency_seconds_max": max(durations),
        },
        "limitations": [
            "CPU/GPU metrics require host-level collection and are not inferred by this probe.",
            "WER/CER remain null when --reference is not provided.",
        ],
    }
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0 if all(item["result"] and item["result"].get("status") == "success" for item in runs) else 1


if __name__ == "__main__":
    raise SystemExit(main())
