import pytest
from pydantic import ValidationError

from backend.app.api.v1.schemas.request_schema import (
    CreateRequestSchema,
    UpdateStatusSchema,
)
from backend.app.domain.value_objects import Priority, RequestType, Status


def _valid_payload(**kwargs) -> dict:
    base = {
    "external_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "type": "technical_support",
    "requester_name": "Test User",
    "email": "test.user@example.com",
    "description": "Sample description for automated testing",
    "priority": "high",
    }
    base.update(kwargs)
    return base



def test_valid_payload_passes():
    schema = CreateRequestSchema(**_valid_payload())
    assert str(schema.external_id) == "f47ac10b-58cc-4372-a567-0e02b2c3d479"
    assert schema.type == RequestType.TECHNICAL_SUPPORT
    assert schema.priority == Priority.HIGH

def test_invalid_email_fails():
    with pytest.raises(ValidationError) as exc_info:
        CreateRequestSchema(**_valid_payload(email="not-an-email"))
    assert "email" in str(exc_info.value).lower()

def test_invalid_type_fails():
    with pytest.raises(ValidationError):
        CreateRequestSchema(**_valid_payload(type="non_existent_type"))

def test_invalid_priority_fails():
    with pytest.raises(ValidationError):
        CreateRequestSchema(**_valid_payload(priority="urgent"))

def test_empty_external_id_fails():
    with pytest.raises(ValidationError):
        CreateRequestSchema(**_valid_payload(external_id=""))

def test_short_description_fails():
    with pytest.raises(ValidationError):
        CreateRequestSchema(**_valid_payload(description="short"))

def test_short_name_fails():
    with pytest.raises(ValidationError):
        CreateRequestSchema(**_valid_payload(requester_name="A"))

def test_missing_field_fails():
    payload = _valid_payload()
    del payload["email"]
    with pytest.raises(ValidationError):
        CreateRequestSchema(**payload)





def test_valid_status_passes():
    schema = UpdateStatusSchema(status="in_progress")
    assert schema.status == Status.IN_PROGRESS

def test_invalid_status_fails():
    with pytest.raises(ValidationError):
        UpdateStatusSchema(status="pendiente")

def test_all_valid_statuses():
    for status in Status:
        schema = UpdateStatusSchema(status=status)
        assert schema.status == status
