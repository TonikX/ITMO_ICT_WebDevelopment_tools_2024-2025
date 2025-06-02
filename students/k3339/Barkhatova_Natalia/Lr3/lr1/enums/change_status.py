from enum import Enum


class ChangeStatus(str, Enum):
    pending = "pending"  # запрос создан, ожидает ответа
    accepted = "accepted"  # владелец книги принял обмен
    rejected = "rejected"  # владелец отказал
    canceled = "canceled"  # отменён одним из участников
    completed = "completed"  # обмен завершён
