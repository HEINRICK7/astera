"""
domain/entities — re-exports only.

Import from here to get all entities in one import:
    from apps.runtime.src.domain.entities import CapabilityDescriptor, Provider, ContextScope
"""
from apps.runtime.src.domain.entities.capability_descriptor import CapabilityDescriptor
from apps.runtime.src.domain.entities.provider import Provider
from apps.runtime.src.domain.entities.context_scope import ContextScope

__all__ = [
    "CapabilityDescriptor",
    "Provider",
    "ContextScope",
]
