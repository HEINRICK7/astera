"""S3-compatible object adapter for immutable raw evidence."""
from __future__ import annotations

from io import BytesIO
from typing import Mapping


class MinioEvidenceObjectStore:
    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
    ) -> None:
        try:
            from minio import Minio
        except ImportError as exc:  # pragma: no cover - deployment dependency
            raise RuntimeError("MinIO persistence requires minio; install requirements.txt") from exc
        normalized_endpoint = endpoint.removeprefix("http://").removeprefix("https://")
        self._client = Minio(
            normalized_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._bucket = bucket
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    def put(
        self,
        object_key: str,
        payload: bytes,
        *,
        content_type: str,
        metadata: Mapping[str, str],
    ) -> None:
        self._client.put_object(
            self._bucket,
            object_key,
            BytesIO(payload),
            length=len(payload),
            content_type=content_type,
            metadata=dict(metadata),
        )

    def get(self, object_key: str) -> bytes | None:
        try:
            response = self._client.get_object(self._bucket, object_key)
        except Exception as exc:
            # MinIO exposes different exception classes across compatible S3
            # implementations; a missing object is the only expected miss.
            if getattr(exc, "code", None) in {"NoSuchKey", "NoSuchBucket"}:
                return None
            raise
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def health_check(self) -> None:
        """Validate object-storage connectivity and bucket availability."""
        if not self._client.bucket_exists(self._bucket):
            raise RuntimeError(f"MinIO bucket is unavailable: {self._bucket}")
