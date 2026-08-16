"""Run the dependency-free baseline for the separate context track."""
from __future__ import annotations

import asyncio
import json

from .context_adapters import DeterministicContextAdapter
from .context_harness import evaluate


def main() -> None:
    result = asyncio.run(evaluate(DeterministicContextAdapter()))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
