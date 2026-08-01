from datetime import timezone

import pytest

from app.domain.entities.solicitud import Solicitud
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


def _solicitud_base(**kwargs) -> Solicitud:
    defaults = {
        "identificador_externo": "EXT-001",
        "tipo": TipoSolicitud.SOPORTE_TECNICO,
        "nombre_solicitante": "David Julio",
        "correo": "david@example.com",
        "descripcion": "Descripción válida del requerimiento",
        "prioridad": Prioridad.MEDIA,
    }
    defaults.update(kwargs)
    return Solicitud(**defaults)


class TestCreacionSolicitud:

    def test_estado_inicial_es_recibida(self):
        s = _solicitud_base()
        assert s.estado == Estado.RECIBIDA

    def test_genera_id_automaticamente(self):
        s = _solicitud_base()
        assert s.id is not None

    def test_ids_distintos_en_instancias_diferentes(self):
        s1 = _solicitud_base()
        s2 = _solicitud_base(identificador_externo="EXT-002")
        assert s1.id != s2.id

    def test_fechas_con_timezone_utc(self):
        s = _solicitud_base()
        assert s.creado_en.tzinfo is not None
        assert s.actualizado_en.tzinfo is not None

    def test_identificador_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="identificador externo"):
            _solicitud_base(identificador_externo="   ")

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(ValueError, match="nombre"):
            _solicitud_base(nombre_solicitante="")

    def test_descripcion_vacia_lanza_error(self):
        with pytest.raises(ValueError, match="descripción"):
            _solicitud_base(descripcion="  ")


class TestActualizarEstado:

    def test_actualiza_estado_correctamente(self):
        s = _solicitud_base()
        s.actualizar_estado(Estado.EN_PROCESO)
        assert s.estado == Estado.EN_PROCESO

    def test_actualiza_timestamp_al_cambiar_estado(self):
        s = _solicitud_base()
        ts_original = s.actualizado_en
        s.actualizar_estado(Estado.COMPLETADA)
        assert s.actualizado_en >= ts_original

    def test_puede_cambiar_a_todos_los_estados(self):
        for estado in Estado:
            s = _solicitud_base()
            s.actualizar_estado(estado)
            assert s.estado == estado
