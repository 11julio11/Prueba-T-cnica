from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.domain.entities.service_request import ServiceRequest
from app.domain.exceptions import DuplicateExternalIdError, RequestNotFoundError
from app.domain.services.request_service import RequestService
from app.domain.value_objects.status import Status
from app.domain.value_objects.priority import Priority
from app.domain.value_objects.request_type import RequestType


class TestCrearSolicitud:

    def test_crea_exitosamente(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = None
        repo_mock.guardar.side_effect = lambda s: s

        resultado = service.create(**datos_validos)

        repo_mock.guardar.assert_called_once()
        assert resultado.external_id == datos_validos["external_id"]
        assert resultado.status == Status.RECEIVED

    def test_lanza_error_si_identificador_duplicado(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock(spec=ServiceRequest)

        with pytest.raises(DuplicateExternalIdError) as exc_info:
            service.create(**datos_validos)

        assert datos_validos["external_id"] in str(exc_info.value)
        repo_mock.guardar.assert_not_called()

    def test_verifica_duplicado_antes_de_guardar(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock()

        with pytest.raises(DuplicateExternalIdError):
            service.create(**datos_validos)

        repo_mock.obtener_por_identificador_externo.assert_called_once_with(
            datos_validos["external_id"]
        )

    def test_asigna_priority_correctamente(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = None
        repo_mock.guardar.side_effect = lambda s: s

        datos_validos["priority"] = Priority.BAJA
        resultado = service.create(**datos_validos)

        assert resultado.priority == Priority.BAJA


class TestObtenerSolicitud:

    def test_retorna_solicitud_existente(self, service, repo_mock, solicitud_existente):
        repo_mock.get_by_id.return_value = solicitud_existente

        resultado = service.obtener(solicitud_existente.id)

        assert resultado.id == solicitud_existente.id
        repo_mock.get_by_id.assert_called_once_with(solicitud_existente.id)

    def test_lanza_error_si_no_existe(self, service, repo_mock):
        repo_mock.get_by_id.return_value = None
        id_inexistente = uuid4()

        with pytest.raises(RequestNotFoundError) as exc_info:
            service.obtener(id_inexistente)

        assert str(id_inexistente) in str(exc_info.value)


class TestActualizarEstado:

    def test_actualiza_status_exitosamente(self, service, repo_mock, solicitud_existente):
        repo_mock.get_by_id.return_value = solicitud_existente
        repo_mock.actualizar.side_effect = lambda s: s

        resultado = service.update_status(solicitud_existente.id, Status.IN_PROGRESS)

        assert resultado.status == Status.IN_PROGRESS
        repo_mock.actualizar.assert_called_once()

    def test_lanza_error_si_solicitud_no_existe(self, service, repo_mock):
        repo_mock.get_by_id.return_value = None

        with pytest.raises(RequestNotFoundError):
            service.update_status(uuid4(), Status.COMPLETED)

        repo_mock.actualizar.assert_not_called()

    def test_no_llama_actualizar_si_no_existe(self, service, repo_mock):
        repo_mock.get_by_id.return_value = None

        with pytest.raises(RequestNotFoundError):
            service.update_status(uuid4(), Status.REJECTED)

        repo_mock.actualizar.assert_not_called()


class TestListarSolicitudes:

    def test_retorna_lista_vacia_sin_registros(self, service, repo_mock):
        repo_mock.list_requests.return_value = []

        resultado = service.list_requests()

        assert resultado == []
        repo_mock.list_requests.assert_called_once()

    def test_pasa_filtros_al_repositorio(self, service, repo_mock):
        repo_mock.list_requests.return_value = []

        service.list_requests(status=Status.RECEIVED, type=RequestType.ACADEMICA)

        repo_mock.list_requests.assert_called_once_with(
            status=Status.RECEIVED,
            type=RequestType.ACADEMICA,
            priority=None,
            limite=100,
            offset=0,
        )

    def test_retorna_todas_las_solicitudes(self, service, repo_mock, solicitud_existente):
        repo_mock.list_requests.return_value = [solicitud_existente, solicitud_existente]

        resultado = service.list_requests()

        assert len(resultado) == 2


class TestDuplicados:
    """Verifies that duplicate external identifiers are rejected correctly."""

    def test_crear_con_identificador_duplicado_lanza_error(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock(spec=ServiceRequest)

        with pytest.raises(DuplicateExternalIdError):
            service.create(**datos_validos)

    def test_no_guarda_si_identificador_duplicado(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = MagicMock(spec=ServiceRequest)

        with pytest.raises(DuplicateExternalIdError):
            service.create(**datos_validos)

        repo_mock.guardar.assert_not_called()

    def test_segundo_registro_distinto_no_falla(self, service, repo_mock, datos_validos):
        repo_mock.obtener_por_identificador_externo.return_value = None
        repo_mock.guardar.side_effect = lambda s: s

        datos_validos["external_id"] = "EXT-UNIQUE-999"
        resultado = service.create(**datos_validos)

        assert resultado.external_id == "EXT-UNIQUE-999"


class TestConsultaInexistente:
    """Verifies behavior when querying records that do not exist."""

    def test_obtener_registro_inexistente_lanza_error(self, service, repo_mock):
        repo_mock.get_by_id.return_value = None
        id_inexistente = uuid4()

        with pytest.raises(RequestNotFoundError) as exc_info:
            service.obtener(id_inexistente)

        assert str(id_inexistente) in str(exc_info.value)

    def test_actualizar_status_de_registro_inexistente_lanza_error(self, service, repo_mock):
        repo_mock.get_by_id.return_value = None

        with pytest.raises(RequestNotFoundError):
            service.update_status(uuid4(), Status.COMPLETED)

        repo_mock.actualizar.assert_not_called()
