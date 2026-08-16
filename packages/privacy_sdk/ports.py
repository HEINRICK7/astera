"""Privacy workflow port."""
from __future__ import annotations

from typing import Protocol

from .models import ConsentRecord, DataSubjectRequest


class PrivacyPort(Protocol):
    def record_consent(self, consent: ConsentRecord) -> None:
        ...

    def request(self, data_subject_request: DataSubjectRequest) -> None:
        ...

    def list_consents(self, organization_id: str, subject_id: str) -> tuple[ConsentRecord, ...]:
        ...

    def list_requests(self, organization_id: str, subject_id: str | None = None) -> tuple[DataSubjectRequest, ...]:
        ...
