from uuid import UUID


class DomainException(Exception):
    """Base para todas las excepciones de dominio."""
    pass


class SolicitudNoEncontrada(DomainException):
    def __init__(self, id: UUID) -> None:
        self.id = id
        super().__init__(f"Solicitud con id '{id}' no encontrada")


class IdentificadorDuplicado(DomainException):
    def __init__(self, identificador_externo: str) -> None:
        self.identificador_externo = identificador_externo
        super().__init__(
            f"Ya existe una solicitud con identificador externo '{identificador_externo}'"
        )


class EstadoInvalido(DomainException):
    def __init__(self, estado: str) -> None:
        super().__init__(f"Estado '{estado}' no es válido")
