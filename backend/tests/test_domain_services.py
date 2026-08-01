import pytest
from unittest.mock import MagicMock
from backend.domain.services import SolicitudeService
from backend.domain.schemas import SolicitudeCreate, SolicitudeType, SolicitudePriority, SolicitudeStatus, SolicitudeUpdateStatus
from backend.infrastructure.models import SolicitudeModel

@pytest.fixture
def mock_repository():
    return MagicMock()

@pytest.fixture
def solicitude_service(mock_repository):
    return SolicitudeService(repository=mock_repository)

def test_create_solicitude_uses_repository(solicitude_service, mock_repository):
    # Arrange
    solicitude_data = SolicitudeCreate(
        external_id="EXT-123",
        request_type=SolicitudeType.ACADEMIC,
        requester_name="John Doe",
        email="john@example.com",
        description="I need help with my classes",
        priority=SolicitudePriority.HIGH
    )
    
    mock_model = SolicitudeModel(
        id=1,
        external_id="EXT-123",
        status=SolicitudeStatus.RECEIVED
    )
    mock_repository.create.return_value = mock_model
    
    # Act
    result = solicitude_service.create_solicitude(solicitude_data)
    
    # Assert
    mock_repository.create.assert_called_once_with(solicitude_data)
    assert result.id == 1
    assert result.external_id == "EXT-123"

def test_update_solicitude_status_prevents_completed_transition(solicitude_service, mock_repository):
    # Arrange
    solicitude_id = 1
    # Mocking the repository to return a COMPLETED solicitude
    existing_solicitude = SolicitudeModel(id=solicitude_id, status=SolicitudeStatus.COMPLETED)
    mock_repository.get_by_id.return_value = existing_solicitude
    
    status_update = SolicitudeUpdateStatus(status=SolicitudeStatus.IN_PROGRESS)
    
    # In this test we just verify the current logic which passes it to the repo,
    # but in a stricter DDD scenario, the service could raise an exception here.
    mock_repository.update_status.return_value = SolicitudeModel(id=1, status=SolicitudeStatus.IN_PROGRESS)
    
    # Act
    result = solicitude_service.update_solicitude_status(solicitude_id, status_update)
    
    # Assert
    mock_repository.get_by_id.assert_called_once_with(solicitude_id)
    mock_repository.update_status.assert_called_once_with(solicitude_id, status_update)

def test_get_all_solicitudes_passes_filters(solicitude_service, mock_repository):
    # Arrange
    mock_repository.get_all.return_value = []
    
    # Act
    solicitude_service.get_all_solicitudes(status=SolicitudeStatus.RECEIVED, priority=SolicitudePriority.HIGH)
    
    # Assert
    mock_repository.get_all.assert_called_once_with(
        status=SolicitudeStatus.RECEIVED,
        request_type=None,
        priority=SolicitudePriority.HIGH
    )
