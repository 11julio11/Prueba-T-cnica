from enum import Enum


class Estado(str, Enum):
    RECIBIDA = "recibida"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    RECHAZADA = "rechazada"
