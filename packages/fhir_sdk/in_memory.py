"""Deterministic FHIR Gateway adapter for contract tests."""
from __future__ import annotations

import base64
from collections import defaultdict
from typing import Sequence
from uuid import uuid4

from .models import FhirBundle, FhirResource


class InMemoryFhirGateway:
    """Implement resource mapping, validation, creation, reading, and bundling."""

    def __init__(self) -> None:
        self._resources: dict[tuple[str, str], FhirResource] = {}
        self._counters: defaultdict[str, int] = defaultdict(int)

    async def validate(self, resource: FhirResource) -> tuple[str, ...]:
        errors: list[str] = []
        payload = resource.to_dict()
        if payload.get("resourceType") != resource.resource_type:
            errors.append("resourceType must match the resource type")
        if resource.resource_id is not None and not resource.resource_id.strip():
            errors.append("id must not be empty")
        if resource.resource_type == "DocumentReference":
            status = payload.get("status")
            if status not in {"current", "superseded", "entered-in-error"}:
                errors.append("DocumentReference.status is invalid")
            content = payload.get("content")
            if not isinstance(content, list) or not content:
                errors.append("DocumentReference.content must contain an attachment")
            else:
                for index, item in enumerate(content):
                    attachment = item.get("attachment") if isinstance(item, dict) else None
                    if not isinstance(attachment, dict):
                        errors.append(f"DocumentReference.content[{index}].attachment is required")
                        continue
                    data = attachment.get("data")
                    url = attachment.get("url")
                    if data is None and not isinstance(url, str):
                        errors.append(f"DocumentReference.content[{index}] needs attachment.data or attachment.url")
                    if data is not None:
                        if not isinstance(data, str):
                            errors.append(f"DocumentReference.content[{index}].attachment.data must be base64 text")
                        else:
                            try:
                                base64.b64decode(data, validate=True)
                            except (ValueError, TypeError):
                                errors.append(f"DocumentReference.content[{index}].attachment.data is not valid base64")
                        if not isinstance(attachment.get("contentType"), str) or not attachment["contentType"].strip():
                            errors.append(f"DocumentReference.content[{index}].attachment.contentType is required with data")
        return tuple(errors)

    async def create(self, resource: FhirResource) -> FhirResource:
        errors = await self.validate(resource)
        if errors:
            raise ValueError("Invalid FHIR resource: " + "; ".join(errors))
        resource_id = resource.resource_id or self._next_id(resource.resource_type)
        created = FhirResource(
            resource_type=resource.resource_type,
            resource_id=resource_id,
            data=resource.to_dict(),
        )
        self._resources[(created.resource_type, resource_id)] = created
        return created

    async def read(self, resource_type: str, resource_id: str) -> FhirResource | None:
        return self._resources.get((resource_type, resource_id))

    async def bundle(
        self,
        resources: Sequence[FhirResource],
        bundle_type: str = "collection",
    ) -> FhirBundle:
        return FhirBundle(bundle_type=bundle_type, entries=tuple(resources))

    def _next_id(self, resource_type: str) -> str:
        self._counters[resource_type] += 1
        return f"{resource_type.lower()}-{self._counters[resource_type]}-{uuid4().hex[:8]}"
