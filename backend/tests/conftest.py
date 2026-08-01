from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.domain.entities.solicitud import Solicitud
from app.domain.ports.solicitud_repository import SolicitudRepository
from app.domain.services.solicitud_service import SolicitudService
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


@pytest.fixture
def repo_mock() -> MagicMock:
    return MagicMock(spec=SolicitudRepository)


@pytest.fixture
def service(repo_mock: MagicMock) -> SolicitudService:
    return SolicitudService(repo=repo_mock)


@pytest.fixture
def datos_validos() -> dict:
    return {
        "identificador_externo": "EXT-001",
        "tipo": TipoSolicitud.SOPORTE_TECNICO,
        "nombre_solicitante": "David Julio",
        "correo": "david@example.com",
        "descripcion": "Necesito acceso al sistema institucional",
        "prioridad": Prioridad.ALTA,
    }


@pytest.fixture
def solicitud_existente(datos_validos: dict) -> Solicitud:
    return Solicitud(**datos_validos)
