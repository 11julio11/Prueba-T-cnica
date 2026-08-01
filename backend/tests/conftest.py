from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.domain.entities.service_request import ServiceRequest
from app.domain.ports.request_repository import RequestRepository
from app.domain.services.request_service import RequestService
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


@pytest.fixture
def repo_mock() -> MagicMock:
    return MagicMock(spec=RequestRepository)


@pytest.fixture
def service(repo_mock: MagicMock) -> RequestService:
    return RequestService(repo=repo_mock)


@pytest.fixture
def datos_validos() -> dict:
    return {
        "external_id": "EXT-001",
        "type": RequestType.SOPORTE_TECNICO,
        "requester_name": "Test User",
        "email": "test.user@example.com",
        "description": "Sample description for automated testing",
        "priority": Priority.ALTA,
    }


@pytest.fixture
def solicitud_existente(datos_validos: dict) -> ServiceRequest:
    return ServiceRequest(**datos_validos)
