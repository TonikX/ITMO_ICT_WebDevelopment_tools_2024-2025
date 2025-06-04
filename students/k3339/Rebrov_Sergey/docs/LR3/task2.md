## **Вызов парсера через очередь**

Были добавлены новые эндпоинты `parse_celery`. Был создан конфигурационный файл `celery_worker.py`, который будет описывать нашу очередь.

`celery_worker.py`:
```python
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["tasks"],
)

celery_app.conf.task_routes = {
    "tasks.parse_and_save_task": {"queue": "parser"},
}
```

Также были обновлены `requirements.txt`, в которые были добавлены необходимые библиотеки, и файл `docker-compose.yml`, в котором добавилось 2 новых контейнера - `worker` для Celery и `redis` для Redis.

`docker-compose.yml`
```dockerfile
services:
  postgres:
    image: postgres:17
    restart: always
    environment:
      POSTGRES_USER: user_lr3
      POSTGRES_PASSWORD: pass_lr3
      POSTGRES_DB: lr3
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  redis:
    image: redis:7
    restart: always
    ports:
      - "6379:6379"

  client:
    build:
      context: ./client
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - postgres
      - parser
    environment:
      DB_ADMIN: postgresql://user_lr3:pass_lr3@postgres:5432/lr3
      PARSER_URL: http://parser:8001
    ports:
      - "8000:8000"

  parser:
    build:
      context: ./parser
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - postgres
      - redis
    environment:
      DB_ADMIN: postgresql://user_lr3:pass_lr3@postgres:5432/lr3
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8001:8001"

  worker:
    build:
      context: ./parser
      dockerfile: Dockerfile
    command: celery -A celery_worker.celery_app worker --loglevel=info --concurrency=1 --queues=parser
    restart: always
    depends_on:
      - redis
      - postgres
    environment:
      DB_ADMIN: postgresql://user_lr3:pass_lr3@postgres:5432/lr3
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./parser:/code

volumes:
  pgdata:
```

После чего эндпоинты были протестированы. Задача для парсера была успешно запущена, а в базе данных появилась новая запись:

 ![Swagger](../imgs/screenshot3.png)
 ![Postgres](../imgs/screenshot4.png)