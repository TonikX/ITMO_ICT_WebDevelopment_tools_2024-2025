# Enum
Для боллее удобной реализации проверки статусов создаются перечисления
```python
class Genres(Enum):
    sci_fi = "Science Fiction"
    non_fi = "Non-fiction"
    Novel = "Novel"

class BookStatuses(Enum):
    available = "available"
    Ordered = "Ordered"
    Exchanged = "Exchanged"
```