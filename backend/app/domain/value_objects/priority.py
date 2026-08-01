from enum import Enum


class Priority(str, Enum):
    BAJA = "low"
    MEDIA = "medium"
    ALTA = "high"
