"""Run the dependency-free baseline benchmark."""
from __future__ import annotations

from .adapters import DeterministicBaselineAdapter
from .harness import print_report, run


if __name__ == "__main__":
    print_report(run(DeterministicBaselineAdapter()))
