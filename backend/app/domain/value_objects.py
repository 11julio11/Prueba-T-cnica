import enum

class Status(enum.StrEnum):
    RECEIVED = enum.auto()
    IN_PROGRESS = enum.auto()
    COMPLETED = enum.auto()
    REJECTED = enum.auto()

class Priority(enum.StrEnum):
    LOW = enum.auto()
    MEDIUM = enum.auto()
    HIGH = enum.auto()

class RequestType(enum.StrEnum):
    PLATFORM_ACCESS = enum.auto()
    TECHNICAL_SUPPORT = enum.auto()
    ACADEMIC = enum.auto()
    ADMINISTRATIVE = enum.auto()
