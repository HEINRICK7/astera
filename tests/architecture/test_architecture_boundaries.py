"""Static architecture fitness tests for the Astera Constitution.

These tests inspect imports instead of importing the Runtime. That keeps the
architecture gate independent from NATS, FastAPI lifespan and external
providers. Known violations are expected to fail until the boundaries are
refactored; do not add exceptions to make the baseline green.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SRC = ROOT / "apps" / "runtime" / "src"
PACKAGES = ROOT / "packages"


@dataclass(frozen=True)
class ImportViolation:
    source: Path
    line: int
    imported: str
    reason: str

    def format(self) -> str:
        relative = self.source.relative_to(ROOT)
        return f"{relative}:{self.line}: {self.imported} ({self.reason})"


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _imports(path: Path) -> list[tuple[int, str, str | None]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[tuple[int, str, str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name, alias.asname) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.extend((node.lineno, node.module, alias.name) for alias in node.names)
    return imports


def _starts_with(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(f"{prefix}.") for prefix in prefixes)


def _violations_for(
    root: Path,
    *,
    module_prefixes: tuple[str, ...],
    reason: str,
    imported_name: bool = False,
) -> list[ImportViolation]:
    violations: list[ImportViolation] = []
    for source in _python_files(root):
        for line, module, name in _imports(source):
            imported = f"{module}.{name}" if imported_name and name else module
            if _starts_with(imported if imported_name else module, module_prefixes):
                violations.append(ImportViolation(source, line, imported, reason))
    return violations


def _assert_clean(violations: list[ImportViolation]) -> None:
    assert not violations, "\n".join(item.format() for item in violations)


def test_domain_does_not_depend_on_outer_layers() -> None:
    violations = _violations_for(
        RUNTIME_SRC / "domain",
        module_prefixes=(
            "apps.runtime.src.application",
            "apps.runtime.src.adapters",
            "apps.runtime.src.infrastructure",
            "apps.runtime.src.presentation",
        ),
        reason="domain must not depend on outer Runtime layers",
    )
    _assert_clean(violations)


def test_application_does_not_depend_on_outer_runtime_layers() -> None:
    violations = _violations_for(
        RUNTIME_SRC / "application",
        module_prefixes=(
            "apps.runtime.src.adapters",
            "apps.runtime.src.infrastructure",
            "apps.runtime.src.presentation",
        ),
        reason="application must depend on ports/contracts, not outer layers",
    )
    _assert_clean(violations)


def test_packages_never_depend_on_apps() -> None:
    violations = _violations_for(
        PACKAGES,
        module_prefixes=("apps",),
        reason="packages are public/shared boundaries and must not import apps",
    )
    _assert_clean(violations)


def test_plugin_sdk_never_depends_on_runtime() -> None:
    violations = _violations_for(
        PACKAGES / "plugin_sdk",
        module_prefixes=("apps.runtime",),
        reason="plugin_sdk must depend on contracts, never on Runtime implementation",
    )
    _assert_clean(violations)


def test_application_does_not_import_in_memory_implementations() -> None:
    concrete_stateful_names = {
        "AuthService",
        "PatientDirectory",
        "EncounterDirectory",
        "WorkspaceDirectory",
        "TimelineDirectory",
        "ClinicalReviewResultStore",
    }
    violations: list[ImportViolation] = []
    for source in _python_files(RUNTIME_SRC / "application"):
        for line, module, name in _imports(source):
            if name and (name.startswith("InMemory") or name in concrete_stateful_names):
                violations.append(
                    ImportViolation(
                        source,
                        line,
                        f"{module}.{name}",
                        "application must consume a port, not a concrete stateful implementation",
                    )
                )
    _assert_clean(violations)


def test_application_does_not_import_forbidden_frameworks_or_vendor_sdks() -> None:
    forbidden = (
        "fastapi",
        "starlette",
        "google",
        "sqlalchemy",
        "asyncpg",
        "redis",
        "nats",
        "minio",
        "qdrant_client",
        "httpx",
        "websockets",
        "opentelemetry",
    )
    violations = _violations_for(
        RUNTIME_SRC / "application",
        module_prefixes=forbidden,
        reason="application must not depend directly on framework/vendor details",
    )
    _assert_clean(violations)


def test_clinical_runtime_does_not_import_legacy_speech_sdk() -> None:
    violations = _violations_for(
        RUNTIME_SRC / "application" / "clinical",
        module_prefixes=("packages.speech_sdk", "apps.runtime.src.adapters.speech"),
        reason="Clinical Runtime consumes canonical evidence, not legacy speech implementation",
    )
    _assert_clean(violations)


def test_bootstrap_does_not_compose_legacy_speech() -> None:
    violations = _violations_for(
        RUNTIME_SRC / "bootstrap",
        module_prefixes=("packages.speech_sdk", "apps.runtime.src.adapters.speech"),
        reason="Astera bootstrap must not own audio/STT provider composition",
    )
    _assert_clean(violations)
