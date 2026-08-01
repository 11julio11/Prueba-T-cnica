from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.domain.entities.solicitud import Solicitud
from app.domain.exceptions import IdentificadorDuplicado, SolicitudNoEncontrada
from app.domain.services.solicitud_service import SolicitudService
from app.domain.value_objects.estado import Estado
from app.domain.value_objects.prioridad import Prioridad
from app.domain.value_objects.tipo_solicitud import TipoSolicitud


class TestCrearSolicitud:

    def test_crea_exitosamente(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = None
        repo_mock.guardar.side_effect = lambda s: s

        resultado = service.crear(**datos_validos)

        repo_mock.guardar.assert_called_once()
        assert resultado.identificador_externo == datos_validos["identificador_externo"]
        assert resultado.estado == Estado.RECIBIDA

    def test_lanza_error_si_identificador_duplicado(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock(spec=Solicitud)

        with pytest.raises(IdentificadorDuplicado) as exc_info:
            service.crear(**datos_validos)

        assert datos_validos["identificador_externo"] in str(exc_info.value)
        repo_mock.guardar.assert_not_called()

    def test_verifica_duplicado_antes_de_guardar(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock()

        with pytest.raises(IdentificadorDuplicado):
            service.crear(**datos_validos)

        repo_mock.obtener_por_identificador_externo.assert_called_once_with(
            datos_validos["identificador_externo"]
        )

    def test_asigna_prioridad_correctamente(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = None
        repo_mock.guardar.side_effect = lambda s: s

        datos_validos["prioridad"] = Prioridad.BAJA
        resultado = service.crear(**datos_validos)

        assert resultado.prioridad == Prioridad.BAJA


class TestObtenerSolicitud:

    def test_retorna_solicitud_existente(self, service, repo_mock, solicitud_existente):
        repo_mock.obtener_por_id.return_value = solicitud_existente

        resultado = service.obtener(solicitud_existente.id)

        assert resultado.id == solicitud_existente.id
        repo_mock.obtener_por_id.assert_called_once_with(solicitud_existente.id)

    def test_lanza_error_si_no_existe(self, service, repo_mock):
        repo_mock.obtener_por_id.return_value = None
        id_inexistente = uuid4()

        with pytest.raises(SolicitudNoEncontrada) as exc_info:
            service.obtener(id_inexistente)

        assert str(id_inexistente) in str(exc_info.value)


class TestActualizarEstado:

    def test_actualiza_estado_exitosamente(self, service, repo_mock, solicitud_existente):
        repo_mock.obtener_por_id.return_value = solicitud_existente
        repo_mock.actualizar.side_effect = lambda s: s

        resultado = service.actualizar_estado(solicitud_existente.id, Estado.EN_PROCESO)

        assert resultado.estado == Estado.EN_PROCESO
        repo_mock.actualizar.assert_called_once()

    def test_lanza_error_si_solicitud_no_existe(self, service, repo_mock):
        repo_mock.obtener_por_id.return_value = None

        with pytest.raises(SolicitudNoEncontrada):
            service.actualizar_estado(uuid4(), Estado.COMPLETADA)

        repo_mock.actualizar.assert_not_called()

    def test_no_llama_actualizar_si_no_existe(self, service, repo_mock):
        repo_mock.obtener_por_id.return_value = None

        with pytest.raises(SolicitudNoEncontrada):
            service.actualizar_estado(uuid4(), Estado.RECHAZADA)

        repo_mock.actualizar.assert_not_called()


class TestListarSolicitudes:

    def test_retorna_lista_vacia_sin_registros(self, service, repo_mock):
        repo_mock.listar.return_value = []

        resultado = service.listar()

        assert resultado == []
        repo_mock.listar.assert_called_once()

    def test_pasa_filtros_al_repositorio(self, service, repo_mock):
        repo_mock.listar.return_value = []

        service.listar(estado=Estado.RECIBIDA, tipo=TipoSolicitud.ACADEMICA)

        repo_mock.listar.assert_called_once_with(
            estado=Estado.RECIBIDA,
            tipo=TipoSolicitud.ACADEMICA,
            prioridad=None,
            limite=100,
            offset=0,
        )

    def test_retorna_todas_las_solicitudes(self, service, repo_mock, solicitud_existente):
        repo_mock.listar.return_value = [solicitud_existente, solicitud_existente]

        resultado = service.listar()

        assert len(resultado) == 2


class TestDuplicados:
    """Verifies that duplicate external identifiers are rejected correctly."""

    def test_crear_con_identificador_duplicado_lanza_error(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock(spec=Solicitud)

        with pytest.raises(IdentificadorDuplicado):
            service.crear(**datos_validos)

    def test_no_guarda_si_identificador_duplicado(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock(spec=Solicitud)

        with pytest.raises(IdentificadorDuplicado):
            service.crear(**datos_validos)

        repo_mock.guardar.assert_not_called()

    def test_segundo_registro_distinto_no_falla(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = None
        repo_mock.guardar.side_effect = lambda s: s

        datos_validos["identificador_externo"] = "EXT-UNIQUE-999"
        resultado = service.crear(**datos_validos)

        assert resultado.identificador_externo == "EXT-UNIQUE-999"


class TestConsultaInexistente:
    """Verifies behavior when querying records that do not exist."""

    def test_obtener_registro_inexistente_lanza_error(self, service, repo_mock):
        repo_mock.obtener_por_id.return_value = None
        id_inexistente = uuid4()

        with pytest.raises(SolicitudNoEncontrada) as exc_info:
            service.obtener(id_inexistente)

        assert str(id_inexistente) in str(exc_info.value)

    def test_actualizar_estado_de_registro_inexistente_lanza_error(self, service, repo_mock):
        repo_mock.obtener_por_id.return_value = None

        with pytest.raises(SolicitudNoEncontrada):
            service.actualizar_estado(uuid4(), Estado.COMPLETADA)

        repo_mock.actualizar.assert_not_called()
