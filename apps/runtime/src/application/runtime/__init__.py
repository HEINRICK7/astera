"""
application/runtime — LEGACY MODULE.

RuntimeManager was replaced by AsteraKernel in Phase C.
This file is kept only for reference during migration.

DO NOT use RuntimeManager in new code.
Use AsteraKernel from apps.runtime.src.application.kernel instead.

Will be removed in Phase D cleanup.
"""
from apps.runtime.src.application.kernel import AsteraKernel as RuntimeManager  # noqa: F401

__all__ = ["RuntimeManager"]
