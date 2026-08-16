"""Shared configuration loading and validation services."""
from __future__ import annotations

from typing import Any, Generic, Mapping, TypeVar

from pydantic import ValidationError
from pydantic_settings import BaseSettings

SettingsT = TypeVar("SettingsT", bound=BaseSettings)


class ConfigurationError(RuntimeError):
    """Raised when a settings model cannot be loaded or validated."""


class ConfigurationLoader(Generic[SettingsT]):
    """Load a typed settings model from environment and explicit overrides."""

    def __init__(self, settings_type: type[SettingsT]) -> None:
        self._settings_type = settings_type

    def load(self, overrides: Mapping[str, Any] | None = None) -> SettingsT:
        """Build and validate settings, preserving Pydantic's env semantics."""
        try:
            return self._settings_type(**dict(overrides or {}))
        except ValidationError as exc:
            raise ConfigurationError(
                f"Invalid configuration for {self._settings_type.__name__}: {exc}"
            ) from exc
