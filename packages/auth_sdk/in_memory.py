"""Development authentication service behind the future Keycloak adapter."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from .models import AuthTokens, LoginCredentials, Principal


class AuthenticationError(Exception):
    """Credentials or refresh token are invalid."""


class AuthorizationError(Exception):
    """The authenticated principal lacks a required permission."""


class InMemoryCredentialStore:
    """Development credential adapter; replaceable by an identity provider."""

    def __init__(self) -> None:
        self._users: dict[str, tuple[bytes, Principal]] = {}

    def register_user(self, credentials: LoginCredentials, principal: Principal) -> None:
        self._users[credentials.email.lower()] = (self._hash_password(credentials.password), principal)

    def authenticate_credentials(self, credentials: LoginCredentials) -> Principal:
        record = self._users.get(credentials.email.lower())
        if record is None or not hmac.compare_digest(
            record[0], self._hash_password(credentials.password)
        ):
            raise AuthenticationError("invalid credentials")

        return record[1]

    @staticmethod
    def _hash_password(password: str) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            b"astera-auth-v1",
            120_000,
        )


class InMemorySessionStore:
    """Development refresh-session adapter with consume-once semantics."""

    def __init__(self) -> None:
        self._refresh_tokens: dict[str, Principal] = {}

    def save(self, session_id: str, principal: Principal) -> None:
        self._refresh_tokens[session_id] = principal

    def consume(self, session_id: str) -> Principal | None:
        return self._refresh_tokens.pop(session_id, None)


class JwtTokenIssuer:
    """JWT adapter responsible only for access-token issue and verification."""

    def __init__(self, *, secret: str, access_ttl_seconds: int = 900) -> None:
        if len(secret) < 32:
            raise ValueError("auth secret must contain at least 32 characters")
        self._secret = secret
        self._access_ttl_seconds = access_ttl_seconds

    def issue(self, principal: Principal) -> AuthTokens:
        now = datetime.now(timezone.utc)
        access = jwt.encode(
            {
                **principal.to_claims(),
                "iat": now,
                "exp": now + timedelta(seconds=self._access_ttl_seconds),
                "typ": "access",
            },
            self._secret,
            algorithm="HS256",
        )
        return AuthTokens(
            access_token=access,
            refresh_token=secrets.token_urlsafe(48),
            expires_in=self._access_ttl_seconds,
        )

    def verify(self, access_token: str) -> Principal:
        try:
            claims = jwt.decode(access_token, self._secret, algorithms=["HS256"])
            return Principal(
                user_id=claims["sub"],
                email=claims["email"],
                organization_id=claims["organization_id"],
                workspace_ids=tuple(claims.get("workspace_ids", [])),
                roles=tuple(claims.get("roles", [])),
                permissions=tuple(claims.get("permissions", [])),
            )
        except (jwt.PyJWTError, KeyError, TypeError) as exc:
            raise AuthenticationError("invalid access token") from exc


class InMemoryAuthenticationService:
    """Compose credential, session and token adapters behind one facade."""

    def __init__(self, *, secret: str, access_ttl_seconds: int = 900) -> None:
        self._credentials = InMemoryCredentialStore()
        self._sessions = InMemorySessionStore()
        self._tokens = JwtTokenIssuer(secret=secret, access_ttl_seconds=access_ttl_seconds)

    def register_user(self, credentials: LoginCredentials, principal: Principal) -> None:
        self._credentials.register_user(credentials, principal)

    def login(self, credentials: LoginCredentials) -> AuthTokens:
        principal = self._credentials.authenticate_credentials(credentials)
        tokens = self._tokens.issue(principal)
        self._sessions.save(tokens.refresh_token, principal)
        return tokens

    def refresh(self, refresh_token: str) -> AuthTokens:
        principal = self._sessions.consume(refresh_token)
        if principal is None:
            raise AuthenticationError("invalid refresh token")
        tokens = self._tokens.issue(principal)
        self._sessions.save(tokens.refresh_token, principal)
        return tokens

    def authenticate(self, access_token: str) -> Principal:
        return self._tokens.verify(access_token)

    def require_permission(self, principal: Principal, permission: str) -> None:
        if permission not in principal.permissions:
            raise AuthorizationError(f"permission required: {permission}")


# Compatibility name for callers migrating from the original facade name.
AuthService = InMemoryAuthenticationService
