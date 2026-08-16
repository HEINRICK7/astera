"""Compatibility-free application agent port location.

The Google ADK implementation lives in ``adapters.agents.google_adk``.
This module intentionally contains no provider implementation.
"""
from __future__ import annotations

from apps.runtime.src.ports.outbound.agent_runtime import AgentRuntimePort

__all__ = ["AgentRuntimePort"]
