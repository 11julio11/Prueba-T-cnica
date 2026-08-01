from enum import Enum


class TipoSolicitud(str, Enum):
    ACCESO_PLATAFORMA = "acceso_plataforma"
    SOPORTE_TECNICO = "soporte_tecnico"
    ACADEMICA = "academica"
    ADMINISTRATIVA = "administrativa"
