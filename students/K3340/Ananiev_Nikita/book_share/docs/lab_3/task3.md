## **Подзадача 3**: Вызов парсера из FastAPI через очередь
### Запуск парсера в фоне улучшит производительность и пользовательский опыт приложения

Сам код запуска представлен в подзадаче 2. Так выглядит файл конфигурации celery:
```python
import os
from celery import Celery
from dotenv import load_dotenv
import requests

load_dotenv()

celery_app = Celery(
    __name__,
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)
```
.env файл, который используется основным приложением и celery воркером:
```
DB_CONN=postgresql://postgres:aventador@db_container/book_share_db
DB_HOST=db_container
DB_PASS=aventador
DB_NAME=book_share_db
REDIS_URL=redis://redis:6379/0
PARSER_URL=http://parser_container:4242/parse
JWT_SECRET_KEY=most_secret_key
```

Dockerfile для celery worker и основного приложения:
```dockerfile
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc

WORKDIR /app

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.11-slim

RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY . .

RUN rm -rf parser lab2

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```