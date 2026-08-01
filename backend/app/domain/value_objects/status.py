from enum import Enum


class Status(str, Enum):
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
