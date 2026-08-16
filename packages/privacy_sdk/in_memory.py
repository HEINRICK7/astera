"""In-memory LGPD workflow with organization-scoped reads."""
from __future__ import annotations

from threading import RLock

from .models import ConsentRecord, DataSubjectRequest


class InMemoryPrivacyService:
    def __init__(self) -> None:
        self._lock = RLock()
        self._consents: list[ConsentRecord] = []
        self._requests: list[DataSubjectRequest] = []

    def record_consent(self, consent: ConsentRecord) -> None:
        with self._lock:
            self._consents.append(consent)

    def request(self, data_subject_request: DataSubjectRequest) -> None:
        with self._lock:
            self._requests.append(data_subject_request)

    def list_consents(self, organization_id: str, subject_id: str) -> tuple[ConsentRecord, ...]:
        with self._lock:
            return tuple(
                consent
                for consent in reversed(self._consents)
                if consent.organization_id == organization_id and consent.subject_id == subject_id
            )

    def list_requests(
        self,
        organization_id: str,
        subject_id: str | None = None,
    ) -> tuple[DataSubjectRequest, ...]:
        with self._lock:
            return tuple(
                request
                for request in reversed(self._requests)
                if request.organization_id == organization_id
                and (subject_id is None or request.subject_id == subject_id)
            )
