from datetime import timezone

import pytest

from app.domain.entities.service_request import ServiceRequest
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


def _solicitud_base(**kwargs) -> ServiceRequest:
    defaults = {
        "external_id": "EXT-001",
        "type": RequestType.SOPORTE_TECNICO,
        "requester_name": "Test User",
        "email": "test.user@example.com",
        "description": "Sample description for automated testing",
        "priority": Priority.MEDIA,
    }
    defaults.update(kwargs)
    return ServiceRequest(**defaults)


class TestCreacionSolicitud:

    def test_status_inicial_es_recibida(self):
        s = _solicitud_base()
        assert s.status == Status.RECEIVED

    def test_genera_id_automaticamente(self):
        s = _solicitud_base()
        assert s.id is not None

    def test_ids_distintos_en_instancias_diferentes(self):
        s1 = _solicitud_base()
        s2 = _solicitud_base(external_id="EXT-002")
        assert s1.id != s2.id

    def test_fechas_con_timezone_utc(self):
        s = _solicitud_base()
        assert s.created_at.tzinfo is not None
        assert s.updated_at.tzinfo is not None

    def test_identificador_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="identificador externo"):
            _solicitud_base(external_id="   ")

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="nombre"):
            _solicitud_base(requester_name="")

    def test_descripcion_vacia_lanza_error(self):
        with pytest.raises(ValueError, match="descripción"):
            _solicitud_base(description="  ")


class TestActualizarEstado:

    def test_actualiza_status_correctamente(self):
        s = _solicitud_base()
        s.update_status(Status.IN_PROGRESS)
        assert s.status == Status.IN_PROGRESS

    def test_actualiza_timestamp_al_cambiar_status(self):
        s = _solicitud_base()
        ts_original = s.updated_at
        s.update_status(Status.COMPLETED)
        assert s.updated_at >= ts_original

    def test_puede_cambiar_a_todos_los_statuss(self):
        for status in Status:
            s = _solicitud_base()
            s.update_status(status)
            assert s.status == status
