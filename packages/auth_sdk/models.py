"""Immutable identity and token contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class LoginCredentials:
    email: str
    password: str

    def __post_init__(self) -> None:
        if "@" not in self.email or not self.password:
            raise ValueError("valid email and password are required")


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    email: str
    organization_id: str
    workspace_ids: tuple[str, ...] = ()
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.user_id.strip() or not self.email.strip() or not self.organization_id.strip():
            raise ValueError("principal identity fields must not be empty")

    def to_claims(self) -> dict[str, Any]:
        return {
            "sub": self.user_id,
            "email": self.email,
            "organization_id": self.organization_id,
            "workspace_ids": list(self.workspace_ids),
            "roles": list(self.roles),
            "permissions": list(self.permissions),
        }


@dataclass(frozen=True, slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
        }
