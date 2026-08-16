"""FHIR Gateway port."""
from __future__ import annotations

from typing import Protocol, Sequence

from .models import FhirBundle, FhirResource


class FhirGateway(Protocol):
    async def validate(self, resource: FhirResource) -> tuple[str, ...]:
        """Return validation errors without persisting the resource."""

    async def create(self, resource: FhirResource) -> FhirResource:
        """Create a resource and return its server-assigned identity."""

    async def read(self, resource_type: str, resource_id: str) -> FhirResource | None:
        """Read a resource by FHIR type and logical id."""

    async def bundle(self, resources: Sequence[FhirResource], bundle_type: str = "collection") -> FhirBundle:
        """Build a FHIR Bundle from resources."""
