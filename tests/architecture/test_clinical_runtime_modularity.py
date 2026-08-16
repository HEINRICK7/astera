"""Fitness tests for the in-repository Clinical Runtime module graph."""
from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "apps" / "runtime" / "src" / "application" / "clinical" / "modules"
EXPECTED = {
    "ingestion",
    "observations",
    "facts",
    "context",
    "correlation",
    "knowledge",
    "research",
    "representation",
    "projections",
}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module.rsplit(".", 1)[-1])
    return result


def _graph() -> dict[str, set[str]]:
    return {
        path.stem: _imports(path) & EXPECTED
        for path in MODULES.glob("*.py")
        if path.stem != "__init__"
    }


def test_all_clinical_runtime_modules_exist() -> None:
    assert {path.stem for path in MODULES.glob("*.py")} >= EXPECTED
    live_stream = MODULES.parent / "live_stream.py"
    orchestrator = MODULES.parent / "orchestrator.py"
    assert len(live_stream.read_text(encoding="utf-8").splitlines()) <= 120
    assert len(orchestrator.read_text(encoding="utf-8").splitlines()) <= 120


def test_clinical_module_graph_is_acyclic() -> None:
    graph = _graph()
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        assert node not in visiting, f"circular Clinical Runtime dependency at {node}"
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, ()):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for module in graph:
        visit(module)


def test_representation_and_projections_do_not_depend_on_transcription() -> None:
    forbidden = {"transcript_state", "normalization", "live_stream", "evidence_ingress"}
    for name in ("representation", "projections"):
        assert not (_imports(MODULES / f"{name}.py") & forbidden)


def test_knowledge_and_research_do_not_own_runtime_flow() -> None:
    forbidden = {"live_stream", "ingestion", "projections"}
    for name in ("knowledge", "research", "correlation"):
        assert not (_imports(MODULES / f"{name}.py") & forbidden)


def test_observations_and_facts_do_not_depend_on_ui() -> None:
    forbidden = {"a2ui_stream", "presentation_composer", "projections"}
    for name in ("observations", "facts", "context"):
        assert not (_imports(MODULES / f"{name}.py") & forbidden)
