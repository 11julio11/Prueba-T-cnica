from enum import Enum


class RequestType(str, Enum):
    ACCESO_PLATAFORMA = "platform_access"
    SOPORTE_TECNICO = "technical_support"
    ACADEMICA = "academic"
    ADMINISTRATIVA = "administrative"
