"""Provider-neutral authentication and authorization contracts."""

from .in_memory import (
    AuthService,
    AuthenticationError,
    AuthorizationError,
    InMemoryAuthenticationService,
    InMemoryCredentialStore,
    InMemorySessionStore,
    JwtTokenIssuer,
)
from .models import AuthTokens, LoginCredentials, Principal

__all__ = [
    "AuthService",
    "AuthTokens",
    "AuthenticationError",
    "AuthorizationError",
    "InMemoryAuthenticationService",
    "InMemoryCredentialStore",
    "InMemorySessionStore",
    "JwtTokenIssuer",
    "LoginCredentials",
    "Principal",
]
