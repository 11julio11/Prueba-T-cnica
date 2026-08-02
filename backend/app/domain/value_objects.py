from enum import StrEnum, auto


class Status(StrEnum):
    RECEIVED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    REJECTED = auto()

class Priority(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()

class RequestType(StrEnum):
    PLATFORM_ACCESS = auto()
    TECHNICAL_SUPPORT = auto()
    ACADEMIC = auto()
    ADMINISTRATIVE = auto()
