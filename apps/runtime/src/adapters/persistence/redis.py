"""Redis adapters for ephemeral, shared runtime state."""
from __future__ import annotations

import json
from typing import Any, Mapping

from packages.auth_sdk import Principal


class RedisClientFactory:
    @staticmethod
    def create(url: str) -> Any:
        try:
            import redis
        except ImportError as exc:  # pragma: no cover - deployment dependency
            raise RuntimeError("Redis persistence requires redis-py; install requirements.txt") from exc
        return redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )


class RedisSessionStateAdapter:
    """Shared TTL-backed implementation of ``SessionStatePort``."""

    def __init__(self, client: Any, *, ttl_seconds: int, key_prefix: str = "astera:session:") -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds
        self._key_prefix = key_prefix

    def get(self, session_id: str) -> Mapping[str, Any] | None:
        value = self._client.get(self._key(session_id))
        return json.loads(value) if value is not None else None

    def save(self, session_id: str, state: Mapping[str, Any]) -> None:
        self._client.set(self._key(session_id), json.dumps(dict(state), default=str), ex=self._ttl_seconds)

    def delete(self, session_id: str) -> None:
        self._client.delete(self._key(session_id))

    def health_check(self) -> None:
        self._client.ping()

    def _key(self, session_id: str) -> str:
        return f"{self._key_prefix}{session_id}"


class RedisRefreshSessionStore:
    """Consume-once refresh-token store shared across Runtime replicas."""

    def __init__(self, client: Any, *, ttl_seconds: int, key_prefix: str = "astera:refresh:") -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds
        self._key_prefix = key_prefix

    def save(self, session_id: str, principal: Principal) -> None:
        self._client.set(
            self._key(session_id),
            json.dumps(principal.to_claims()),
            ex=self._ttl_seconds,
        )

    def consume(self, session_id: str) -> Principal | None:
        key = self._key(session_id)
        pipe = self._client.pipeline()
        pipe.get(key)
        pipe.delete(key)
        value, _ = pipe.execute()
        if value is None:
            return None
        claims = json.loads(value)
        return Principal(
            user_id=claims["sub"],
            email=claims["email"],
            organization_id=claims["organization_id"],
            workspace_ids=tuple(claims.get("workspace_ids", [])),
            roles=tuple(claims.get("roles", [])),
            permissions=tuple(claims.get("permissions", [])),
        )

    def health_check(self) -> None:
        self._client.ping()

    def _key(self, session_id: str) -> str:
        return f"{self._key_prefix}{session_id}"
