"""Versioned NIEDE PT-BR context-rule asset loading."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


RULES_PATH = Path(__file__).with_name("data") / "pt_br_context_rules_v1.json"


def load_context_rules(path: Path = RULES_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("language") != "pt-BR" or not payload.get("rules"):
        raise ValueError(f"Invalid PT-BR context-rule asset: {path}")
    return payload


def asset_sha256(path: Path = RULES_PATH) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
