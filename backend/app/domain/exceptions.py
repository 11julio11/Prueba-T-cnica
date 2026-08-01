from uuid import UUID


class DomainException(Exception):
    """Base para todas las excepciones de dominio."""
    pass


class RequestNotFoundError(DomainException):
    def __init__(self, id: UUID) -> None:
        self.id = id
        super().__init__(f"ServiceRequest con id '{id}' no encontrada")


class DuplicateExternalIdError(DomainException):
    def __init__(self, external_id: str) -> None:
        self.external_id = external_id
        super().__init__(
            f"Ya existe una request con identificador externo '{external_id}'"
        )


class InvalidStatusError(DomainException):
    def __init__(self, status: str) -> None:
        super().__init__(f"Status '{status}' no es válido")
