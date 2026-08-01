import pytest
from pydantic import ValidationError

from app.api.v1.schemas.request_schema import ActualizarEstadoRequest, CrearSolicitudRequest
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


def _payload_valido(**kwargs) -> dict:
    base = {
        "external_id": "EXT-001",
        "type": "technical_support",
        "requester_name": "Test User",
        "email": "test.user@example.com",
        "description": "Sample description for automated testing",
        "priority": "high",
    }
    base.update(kwargs)
    return base


class TestCrearSolicitudRequest:

    def test_payload_valido_pasa(self):
        schema = CrearSolicitudRequest(**_payload_valido())
        assert schema.external_id == "EXT-001"
        assert schema.type == RequestType.SOPORTE_TECNICO
        assert schema.priority == Priority.ALTA

    def test_correo_invalido_falla(self):
        with pytest.raises(ValidationError) as exc_info:
            CrearSolicitudRequest(**_payload_valido(email="no-es-un-email"))
        assert "email" in str(exc_info.value).lower() or "email" in str(exc_info.value).lower()

    def test_tipo_invalido_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(type="tipo_inexistente"))

    def test_priority_invalida_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(priority="urgente"))

    def test_identificador_externo_vacio_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(external_id=""))

    def test_identificador_solo_espacios_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(external_id="   "))

    def test_descripcion_muy_corta_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(description="corta"))

    def test_nombre_muy_corto_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(requester_name="A"))

    def test_campo_faltante_falla(self):
        payload = _payload_valido()
        del payload["email"]
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**payload)

    def test_limpia_espacios_en_identificador(self):
        schema = CrearSolicitudRequest(**_payload_valido(external_id="  EXT-001  "))
        assert schema.external_id == "EXT-001"


class TestActualizarEstadoRequest:

    def test_status_valido_pasa(self):
        schema = ActualizarEstadoRequest(status="in_progress")
        assert schema.status == Status.IN_PROGRESS

    def test_status_invalido_falla(self):
        with pytest.raises(ValidationError):
            ActualizarEstadoRequest(status="pendiente")

    def test_todos_los_statuss_validos(self):
        for status in Status:
            schema = ActualizarEstadoRequest(status=status)
            assert schema.status == status
