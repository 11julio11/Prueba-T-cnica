from enum import Enum


class Status(str, Enum):
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RequestType(str, Enum):
    PLATFORM_ACCESS = "platform_access"
    TECHNICAL_SUPPORT = "technical_support"
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
