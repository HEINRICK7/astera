"""Deterministic configuration posture checks."""
from __future__ import annotations

from .models import SecurityCheck, SecurityReport


class SecurityPosture:
    """Evaluate baseline runtime controls without exposing secret values."""

    def evaluate(
        self,
        *,
        environment: str,
        auth_secret: str,
        debug: bool,
        docs_enabled: bool,
    ) -> SecurityReport:
        checks = [
            SecurityCheck(
                name="auth_secret_strength",
                status="pass" if len(auth_secret) >= 32 else "fail",
                detail="JWT signing secret meets the minimum length requirement."
                if len(auth_secret) >= 32
                else "JWT signing secret is shorter than the required minimum.",
            ),
            SecurityCheck(
                name="development_secret_not_used_in_production",
                status=(
                    "fail"
                    if environment == "production"
                    and auth_secret == "astera-development-secret-change-in-production"
                    else "pass"
                ),
                detail=(
                    "Production must provide ASTERA_AUTH_SECRET."
                    if environment == "production"
                    and auth_secret == "astera-development-secret-change-in-production"
                    else "No development signing secret detected in production."
                ),
            ),
            SecurityCheck(
                name="debug_disabled_in_production",
                status="fail" if environment == "production" and debug else "pass",
                detail=(
                    "Debug mode must be disabled in production."
                    if environment == "production" and debug
                    else "Debug mode is compatible with the selected environment."
                ),
            ),
            SecurityCheck(
                name="api_docs_disabled_in_production",
                status="fail" if environment == "production" and docs_enabled else "pass",
                detail=(
                    "Interactive API documentation must be disabled in production."
                    if environment == "production" and docs_enabled
                    else "Interactive API documentation policy is satisfied."
                ),
            ),
        ]
        return SecurityReport(environment=environment, checks=tuple(checks))
