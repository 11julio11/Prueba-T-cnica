import pytest
from pydantic import ValidationError

from app.api.v1.schemas.solicitud_request import ActualizarEstadoRequest, CrearSolicitudRequest
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


def _payload_valido(**kwargs) -> dict:
    base = {
        "identificador_externo": "EXT-001",
        "tipo": "soporte_tecnico",
        "nombre_solicitante": "David Julio",
        "correo": "david@example.com",
        "descripcion": "Necesito acceso al sistema institucional",
        "prioridad": "alta",
    }
    base.update(kwargs)
    return base


class TestCrearSolicitudRequest:

    def test_payload_valido_pasa(self):
        schema = CrearSolicitudRequest(**_payload_valido())
        assert schema.identificador_externo == "EXT-001"
        assert schema.tipo == TipoSolicitud.SOPORTE_TECNICO
        assert schema.prioridad == Prioridad.ALTA

    def test_correo_invalido_falla(self):
        with pytest.raises(ValidationError) as exc_info:
            CrearSolicitudRequest(**_payload_valido(correo="no-es-un-correo"))
        assert "correo" in str(exc_info.value).lower() or "email" in str(exc_info.value).lower()

    def test_tipo_invalido_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(tipo="tipo_inexistente"))

    def test_prioridad_invalida_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(prioridad="urgente"))

    def test_identificador_externo_vacio_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(identificador_externo=""))

    def test_identificador_solo_espacios_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(identificador_externo="   "))

    def test_descripcion_muy_corta_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(descripcion="corta"))

    def test_nombre_muy_corto_falla(self):
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**_payload_valido(nombre_solicitante="A"))

    def test_campo_faltante_falla(self):
        payload = _payload_valido()
        del payload["correo"]
        with pytest.raises(ValidationError):
            CrearSolicitudRequest(**payload)

    def test_limpia_espacios_en_identificador(self):
        schema = CrearSolicitudRequest(**_payload_valido(identificador_externo="  EXT-001  "))
        assert schema.identificador_externo == "EXT-001"


class TestActualizarEstadoRequest:

    def test_estado_valido_pasa(self):
        schema = ActualizarEstadoRequest(estado="en_proceso")
        assert schema.estado == Estado.EN_PROCESO

    def test_estado_invalido_falla(self):
        with pytest.raises(ValidationError):
            ActualizarEstadoRequest(estado="pendiente")

    def test_todos_los_estados_validos(self):
        for estado in Estado:
            schema = ActualizarEstadoRequest(estado=estado)
            assert schema.estado == estado
