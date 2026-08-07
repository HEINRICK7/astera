"""
Astera Domain Exceptions.

All exceptions in the Astera platform inherit from AsteraError.
No module raises generic Python exceptions directly — always use domain exceptions.
"""
from __future__ import annotations


class AsteraError(Exception):
    """Base exception for all Astera platform errors."""

    def __init__(self, message: str, code: str = "ASTERA_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


# ── Runtime Exceptions ────────────────────────────────────────────────────────

class RuntimeError(AsteraError):
    """Raised when the Runtime encounters an unrecoverable state."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="RUNTIME_ERROR")


class RuntimeNotReadyError(AsteraError):
    """Raised when an operation is attempted before the Runtime is ready."""

    def __init__(self) -> None:
        super().__init__(
            "The Astera Runtime is not ready. Ensure startup completed successfully.",
            code="RUNTIME_NOT_READY",
        )


# ── Configuration Exceptions ──────────────────────────────────────────────────

class ConfigurationError(AsteraError):
    """Raised when a configuration value is invalid or missing."""

    def __init__(self, key: str, reason: str) -> None:
        super().__init__(
            f"Configuration error for key '{key}': {reason}",
            code="CONFIG_ERROR",
        )
        self.key = key


# ── Plugin Exceptions ─────────────────────────────────────────────────────────

class PluginError(AsteraError):
    """Base exception for plugin-related errors."""

    def __init__(self, plugin_name: str, message: str) -> None:
        super().__init__(f"Plugin '{plugin_name}': {message}", code="PLUGIN_ERROR")
        self.plugin_name = plugin_name


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin is not registered."""

    def __init__(self, plugin_name: str) -> None:
        super().__init__(plugin_name, "not found in the Plugin Registry.")
        self.code = "PLUGIN_NOT_FOUND"


class PluginAlreadyRegisteredError(PluginError):
    """Raised when attempting to register a plugin that is already registered."""

    def __init__(self, plugin_name: str) -> None:
        super().__init__(plugin_name, "is already registered.")
        self.code = "PLUGIN_ALREADY_REGISTERED"


# ── Event Bus Exceptions ──────────────────────────────────────────────────────

class EventBusError(AsteraError):
    """Raised when the Event Bus encounters an error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="EVENT_BUS_ERROR")


class EventBusNotConnectedError(EventBusError):
    """Raised when publishing/subscribing before the Event Bus is connected."""

    def __init__(self) -> None:
        super().__init__(
            "Event Bus is not connected. Ensure NATS connection was established during startup."
        )
        self.code = "EVENT_BUS_NOT_CONNECTED"
