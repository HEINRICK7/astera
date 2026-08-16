"""Terminology provider port."""
from __future__ import annotations

from typing import Protocol

from .models import TerminologyQuery, TerminologyResult


class TerminologyService(Protocol):
    async def lookup(self, query: TerminologyQuery) -> TerminologyResult:
        """Resolve a code or text against a terminology provider."""
