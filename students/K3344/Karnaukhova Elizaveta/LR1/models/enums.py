from enum import Enum


class ExchangeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"


class BookStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
