"""
PluginProtocol — structural contract that all Astera Plugins must implement.

WHY a Protocol (not ABC):
    Plugins are developed independently and loaded dynamically.
    They should not be forced to import from the Kernel SDK.
    Python's Protocol enables structural subtyping — if it looks like a Plugin,
    it IS a Plugin, regardless of inheritance.

Phase D: Plugin SDK will enforce this contract via a base class wrapper.
Phase C: Only the Protocol definition exists here.
"""
from __future__ import annotations

from packages.plugin_sdk import PluginProtocol
