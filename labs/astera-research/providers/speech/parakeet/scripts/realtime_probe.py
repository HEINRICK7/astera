#!/usr/bin/env python3
"""Execute a real NVIDIA Speech NIM realtime WebSocket request."""

from __future__ import annotations

import argparse
import asyncio
import base64
import copy
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
import websockets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", required=True, type=Path, help="PCM16 mono file")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--language", default=os.getenv("PARAKEET_LANGUAGE", "en-US"))
    parser.add_argument("--model", default=os.getenv("PARAKEET_MODEL") or None)
    parser.add_argument("--sample-rate", default=16000, type=int)
    parser.add_argument("--chunk-bytes", default=6400, type=int)
    parser.add_argument("--url", default=os.getenv("PARAKEET_WS_URL", "ws://localhost:9000/v1/realtime?intent=transcription"))
    parser.add_argument("--http-url", default=os.getenv("PARAKEET_HTTP_URL", "http://localhost:9000"))
    parser.add_argument("--timeout", default=float(os.getenv("PARAKEET_TIMEOUT_SECONDS", "60")), type=float)
    parser.add_argument("--enable-word-time-offsets", action="store_true")
    parser.add_argument("--enable-diarization", action="store_true")
    parser.add_argument("--word-boost", action="append", default=[])
    return parser.parse_args()


def event(event_type: str, **fields: Any) -> dict[str, Any]:
    return {"event_id": f"event_{uuid.uuid4()}", "type": event_type, **fields}


def write_events(events: list[dict[str, Any]], output: Path | None) -> None:
    encoded = "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in events)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


async def run(args: argparse.Namespace) -> int:
    if not args.audio.is_file():
        raise SystemExit(f"Áudio não encontrado: {args.audio}")
    audio = args.audio.read_bytes()
    if len(audio) % 2:
        raise SystemExit("PCM16 inválido: o arquivo deve conter número par de bytes.")

    request_id = str(uuid.uuid4())
    events: list[dict[str, Any]] = []
    started = time.perf_counter()
    session_url = args.http_url.rstrip("/") + "/v1/realtime/transcription_sessions"

    # The official endpoint returns the initial session shape. We use that
    # shape and override only explicitly requested experiment parameters.
    async with httpx.AsyncClient(timeout=args.timeout) as client:
        session_response = await client.post(session_url, headers={"x-lab-request-id": request_id})
        session_response.raise_for_status()
        session = session_response.json()

    session = copy.deepcopy(session)
    session["modalities"] = ["text"]
    session["input_audio_format"] = "pcm16"
    session.setdefault("input_audio_transcription", {})["language"] = args.language
    if args.model:
        session["input_audio_transcription"]["model"] = args.model
    session["input_audio_params"] = {"sample_rate_hz": args.sample_rate, "num_channels": 1}
    session.setdefault("recognition_config", {})["enable_word_time_offsets"] = args.enable_word_time_offsets
    session.setdefault("speaker_diarization", {})["enable_speaker_diarization"] = args.enable_diarization
    if args.word_boost:
        session["word_boosting"] = {
            "enable_word_boosting": True,
            "word_boosting_list": args.word_boost,
        }

    async with websockets.connect(args.url, open_timeout=args.timeout) as socket:
        await socket.send(json.dumps(event("transcription_session.update", session=session)))
        for offset in range(0, len(audio), args.chunk_bytes):
            chunk = audio[offset : offset + args.chunk_bytes]
            await socket.send(json.dumps(event("input_audio_buffer.append", audio=base64.b64encode(chunk).decode("ascii"))))
        await socket.send(json.dumps(event("input_audio_buffer.commit")))
        await socket.send(json.dumps(event("input_audio_buffer.done")))

        while True:
            raw = await asyncio.wait_for(socket.recv(), timeout=args.timeout)
            received = json.loads(raw)
            received["received_at_seconds"] = round(time.perf_counter() - started, 6)
            events.append(received)
            if received.get("type") in {
                "conversation.item.input_audio_transcription.completed",
                "conversation.item.input_audio_transcription.failed",
                "error",
            }:
                break

    envelope = {
        "run_id": request_id,
        "protocol": "websocket-realtime",
        "provider": "nvidia-speech-nim",
        "audio": args.audio.name,
        "language": args.language,
        "model": args.model,
        "sample_rate": args.sample_rate,
        "duration_seconds": round(time.perf_counter() - started, 6),
        "events": events,
    }
    write_events([envelope], args.output)
    return 0 if not any(item.get("type") in {"error", "conversation.item.input_audio_transcription.failed"} for item in events) else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run(parse_args())))
