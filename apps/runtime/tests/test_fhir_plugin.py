"""Tests for the FHIR Plugin boundary."""
from __future__ import annotations

import unittest

from apps.runtime.src.application.capabilities.registry import CapabilityRegistry
from apps.runtime.src.application.plugins.fhir import FhirPlugin
from apps.runtime.src.application.providers.registry import ProviderRegistry
from apps.runtime.src.application.providers.resolver import PluginResolver
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from packages.fhir_sdk import InMemoryFhirGateway


class FhirPluginTests(unittest.IsolatedAsyncioTestCase):
    async def test_plugin_validates_creates_reads_and_bundles(self) -> None:
        capabilities = CapabilityRegistry()
        providers = ProviderRegistry()
        resolver = PluginResolver()
        plugin = FhirPlugin(capabilities, providers, resolver, InMemoryFhirGateway())
        resource = {
            "resourceType": "Patient",
            "id": "patient-1",
            "name": [{"family": "Silva", "given": ["Ana"]}],
        }

        await plugin.on_start()
        validated = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.MEDICAL_FHIR,
            {"operation": "validate", "resource": resource},
            {},
        )
        created = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.MEDICAL_FHIR,
            {"operation": "create", "resource": resource},
            {},
        )
        read = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.MEDICAL_FHIR,
            {"operation": "read", "resource_type": "Patient", "resource_id": "patient-1"},
            {},
        )
        bundle = await plugin.invoke(
            plugin.provider_name,
            CapabilityType.MEDICAL_FHIR,
            {"operation": "bundle", "resources": [resource]},
            {},
        )

        self.assertTrue(validated["valid"])
        self.assertEqual(created["resource"]["resourceType"], "Patient")
        self.assertEqual(read["resource"]["id"], "patient-1")
        self.assertEqual(bundle["bundle"]["total"], 1)
        self.assertTrue(capabilities.has_capability(CapabilityType.MEDICAL_FHIR))
        self.assertTrue(providers.get(plugin.provider_name).is_active())

        await plugin.on_stop()
        self.assertFalse(resolver.is_bound(plugin.provider_name))
