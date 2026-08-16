"""
domain/exceptions — re-exports only.

Import from here to get any exception in one import:
    from apps.runtime.src.domain.exceptions import CapabilityNotFoundError, ...
"""
from apps.runtime.src.domain.exceptions.base import AsteraError
from apps.runtime.src.domain.exceptions.runtime_not_ready import RuntimeNotReadyError
from apps.runtime.src.domain.exceptions.event_bus_error import EventBusError
from apps.runtime.src.domain.exceptions.event_bus_not_connected import EventBusNotConnectedError
from apps.runtime.src.domain.exceptions.capability_not_found import CapabilityNotFoundError
from apps.runtime.src.domain.exceptions.no_healthy_provider import NoHealthyProviderError
from apps.runtime.src.domain.exceptions.provider_not_found import ProviderNotFoundError
from apps.runtime.src.domain.exceptions.plugin_not_found import PluginNotFoundError
from apps.runtime.src.domain.exceptions.plugin_load_error import PluginLoadError
from apps.runtime.src.domain.exceptions.task_execution_error import TaskExecutionError
from apps.runtime.src.domain.exceptions.context_not_found import ContextNotFoundError

__all__ = [
    "AsteraError",
    "RuntimeNotReadyError",
    "EventBusError",
    "EventBusNotConnectedError",
    "CapabilityNotFoundError",
    "NoHealthyProviderError",
    "ProviderNotFoundError",
    "PluginNotFoundError",
    "PluginLoadError",
    "TaskExecutionError",
    "ContextNotFoundError",
]
