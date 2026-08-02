from uuid import UUID


class DomainException(Exception):
    """Base para todas las excepciones de dominio."""

class RequestNotFoundError(DomainException):
    def __init__(self, id: UUID | str) -> None:
        self.id = id
        super().__init__(f"Request with id/external_id '{id}' not found")

class DuplicateExternalIdError(DomainException):
    def __init__(self, external_id: str) -> None:
        self.external_id = external_id
        super().__init__(
            f"A request with external_id '{external_id}' already exists"
        )

class InvalidStatusError(DomainException):
    def __init__(self, status: str) -> None:
        super().__init__(f"Status '{status}' is invalid")

class InvalidStatusTransitionError(DomainException):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"Invalid status transition from '{current}' to '{target}'")
