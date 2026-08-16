#!/usr/bin/env python3
"""Execute a real NVIDIA Speech NIM HTTP batch request."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import time
import uuid
from pathlib import Path
from typing import Any

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--language", default=os.getenv("PARAKEET_LANGUAGE", "en-US"))
    parser.add_argument("--model", default=os.getenv("PARAKEET_MODEL") or None)
    parser.add_argument("--url", default=os.getenv("PARAKEET_HTTP_URL", "http://localhost:9000"))
    parser.add_argument(
        "--timeout",
        default=float(os.getenv("PARAKEET_TIMEOUT_SECONDS", "60")),
        type=float,
    )
    return parser.parse_args()


def write_result(result: dict[str, Any], output: Path | None) -> None:
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)


def main() -> int:
    args = parse_args()
    if not args.audio.is_file():
        raise SystemExit(f"Audio não encontrado: {args.audio}")

    request_id = str(uuid.uuid4())
    url = args.url.rstrip("/") + "/v1/audio/transcriptions"
    content_type = mimetypes.guess_type(args.audio.name)[0] or "application/octet-stream"
    form = {"language": args.language}
    if args.model:
        form["model"] = args.model

    started = time.perf_counter()
    try:
        with args.audio.open("rb") as audio, httpx.Client(timeout=args.timeout) as client:
            response = client.post(
                url,
                data=form,
                files={"file": (args.audio.name, audio, content_type)},
                headers={"x-lab-request-id": request_id},
            )
        response.raise_for_status()
        payload: Any = response.json()
        status = "success"
        error = None
    except (httpx.HTTPError, ValueError) as exc:
        payload = None
        status = "failed"
        error = {"type": type(exc).__name__, "message": str(exc)}

    result = {
        "run_id": request_id,
        "protocol": "http-batch",
        "provider": "nvidia-speech-nim",
        "audio": args.audio.name,
        "language": args.language,
        "model": args.model,
        "started_at_unix": started,
        "duration_seconds": round(time.perf_counter() - started, 6),
        "status": status,
        "response": payload,
        "error": error,
    }
    write_result(result, args.output)
    return 0 if status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
