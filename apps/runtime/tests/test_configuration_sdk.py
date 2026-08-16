"""Tests for the shared Configuration SDK."""
from __future__ import annotations

import os
import unittest

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.shared.config import ConfigurationError, ConfigurationLoader


class ExampleSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASTERA_TEST_")

    port: int = Field(default=8000, ge=1, le=65535)
    environment: str = "test"


class ConfigurationLoaderTests(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop("ASTERA_TEST_PORT", None)

    def test_loads_environment_and_explicit_overrides(self) -> None:
        os.environ["ASTERA_TEST_PORT"] = "9000"
        loader = ConfigurationLoader(ExampleSettings)

        from_environment = loader.load()
        overridden = loader.load({"port": 9100})

        self.assertEqual(from_environment.port, 9000)
        self.assertEqual(overridden.port, 9100)

    def test_wraps_validation_errors(self) -> None:
        with self.assertRaises(ConfigurationError):
            ConfigurationLoader(ExampleSettings).load({"port": 0})

