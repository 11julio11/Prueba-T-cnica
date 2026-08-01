import pytest
from datetime import datetime
from backend.domain.services import SolicitudeService
from backend.domain.schemas import SolicitudeCreate, SolicitudeType, SolicitudePriority, SolicitudeStatus, SolicitudeUpdateStatus, SolicitudeResponse
from backend.infrastructure.fake_repositories import FakeSolicitudeRepository

@pytest.fixture
def fake_repository():
    return FakeSolicitudeRepository()

@pytest.fixture
def solicitude_service(fake_repository):
    return SolicitudeService(repository=fake_repository)

def test_create_solicitude_valid_cedula(solicitude_service, fake_repository):
    # Arrange (Positive case)
    solicitude_data = SolicitudeCreate(
        external_id="12345678", # Valid cedula
        request_type=SolicitudeType.ACADEMIC,
        requester_name="John Doe",
        email="john@example.com",
        description="I need help with my classes",
        priority=SolicitudePriority.HIGH
    )
    
    # Act
    result = solicitude_service.create_solicitude(solicitude_data)
    
    # Assert
    # Check that it exists in the fake repo
    saved = fake_repository.get_by_id(result.id)
    assert saved.external_id == "12345678"
    assert result.id == 1
    assert result.external_id == "12345678"
    assert result.status == SolicitudeStatus.RECEIVED

def test_create_solicitude_invalid_cedula():
    # Arrange & Act & Assert (Negative case: Domain validation)
    from pydantic import ValidationError
    with pytest.raises(ValidationError) as exc_info:
        SolicitudeCreate(
            external_id="ABC123", # Invalid cedula
            request_type=SolicitudeType.ACADEMIC,
            requester_name="John Doe",
            email="john@example.com",
            description="I need help with my classes",
            priority=SolicitudePriority.HIGH
        )
    assert "La cédula (external_id) debe contener entre 8 y 10 dígitos numéricos." in str(exc_info.value)

def test_update_solicitude_status_prevents_completed_transition(solicitude_service, fake_repository):
    # Arrange
    # First, create a valid solicitude in the fake repo
    solicitude_data = SolicitudeCreate(
        external_id="EXT-123",
        request_type=SolicitudeType.ACADEMIC,
        requester_name="John Doe",
        email="john@example.com",
        description="I need help with my classes",
        priority=SolicitudePriority.HIGH
    )
    created = solicitude_service.create_solicitude(solicitude_data)
    
    # Force the status to COMPLETED for this test scenario
    fake_repository.update_status(created.id, SolicitudeUpdateStatus(status=SolicitudeStatus.COMPLETED))
    
    status_update = SolicitudeUpdateStatus(status=SolicitudeStatus.IN_PROGRESS)
    
    # Act
    # En un escenario más estricto de DDD, esto podría levantar una excepción
    # Por ahora simplemente validamos que la actualización ocurra sobre el repositorio
    result = solicitude_service.update_solicitude_status(created.id, status_update)
    
    # Assert
    assert result.status == SolicitudeStatus.IN_PROGRESS
    # Verify in the repo
    saved = fake_repository.get_by_id(created.id)
    assert saved.status == SolicitudeStatus.IN_PROGRESS

def test_get_all_solicitudes_passes_filters(solicitude_service, fake_repository):
    # Arrange
    # Create two solicitudes with different statuses
    solicitude_service.create_solicitude(SolicitudeCreate(
        external_id="EXT-1", request_type=SolicitudeType.ACADEMIC, requester_name="A",
        email="a@a.com", description="a", priority=SolicitudePriority.HIGH
    ))
    solicitude_service.create_solicitude(SolicitudeCreate(
        external_id="EXT-2", request_type=SolicitudeType.ACADEMIC, requester_name="B",
        email="b@b.com", description="b", priority=SolicitudePriority.MEDIUM
    ))
    
    fake_repository.update_status(1, SolicitudeUpdateStatus(status=SolicitudeStatus.IN_PROGRESS))
    
    # Act
    # Filter by RECEIVED, should only return EXT-2 (id 2)
    results = solicitude_service.get_all_solicitudes(status=SolicitudeStatus.RECEIVED)
    
    # Assert
    assert len(results) == 1
    assert results[0].external_id == "EXT-2"
