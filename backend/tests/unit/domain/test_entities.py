import pytest

from app.domain.entities import InstitutionalRequest
from app.domain.value_objects import Status, Priority, RequestType
from app.domain.exceptions import InvalidStatusTransitionError

def test_institutional_request_creation(valid_data):
    request = InstitutionalRequest(**valid_data)
    
    assert request.external_id == "EXT-001"
    assert request.status == Status.RECEIVED
    assert request.priority == Priority.HIGH
    assert request.type == RequestType.TECHNICAL_SUPPORT
    assert request.created_at is not None
    assert request.updated_at is not None

def test_institutional_request_update_status():
    request = InstitutionalRequest(
        external_id="EXT-001",
        type=RequestType.TECHNICAL_SUPPORT,
        requester_name="Test",
        email="test@test.com",
        description="Test",
        priority=Priority.HIGH
    )
    
    request.update_status(Status.IN_PROGRESS)
    assert request.status == Status.IN_PROGRESS

    request.update_status(Status.COMPLETED)
    assert request.status == Status.COMPLETED

def test_institutional_request_invalid_status_transition():
    request = InstitutionalRequest(
        external_id="EXT-001",
        type=RequestType.TECHNICAL_SUPPORT,
        requester_name="Test",
        email="test@test.com",
        description="Test",
        priority=Priority.HIGH
    )
    
    request.update_status(Status.COMPLETED)
    
    with pytest.raises(InvalidStatusTransitionError):
        request.update_status(Status.RECEIVED)
