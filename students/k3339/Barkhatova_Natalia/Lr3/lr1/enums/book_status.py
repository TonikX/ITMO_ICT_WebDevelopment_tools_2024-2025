from enum import Enum


class BookStatus(str, Enum):
    available = "available"  # доступна для обмена
    requested = "requested"  # кто-то запросил обмен
    exchanged = "exchanged"  # книга обменяна
    reserved = "reserved"  # зарезервирована
    unavailable = "unavailable"  # временно недоступна
