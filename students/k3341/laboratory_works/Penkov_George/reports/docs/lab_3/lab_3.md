# Лабораторная работа 3: Упаковка FastAPI приложения в Docker, Работа с источниками данных и Очереди

# Выполнение работы

1. Было реализовано следующие fastapi приложения для парсера из лр2:

```python
@app.post("/parse")
async def parse(url: str):
    try:
        await parse_and_save(url)
        return {"message": "Parsing completed!"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

```

2. Созданы Dockerfile для 2х приложений fastapi - lab_1 и lab_3:

Lab_1
```Dockerfile
FROM python:3.13 as requirements-stage

WORKDIR /tmp

RUN pip install poetry && poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.13

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./lab_1 /code/lab_1

CMD ["uvicorn", "lab_1.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

lab_3
```Dockerfile
FROM python:3.13 as requirements-stage

WORKDIR /tmp

RUN pip install poetry && poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.13

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
```

3. Написан docker-compose файл для 3-х контейнеров: lab_1, lab_3, бд:

```yml  
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "6543:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data

  lab_1:
    build:
      context: ../lab_1
    container_name: lab_1
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    env_file: .env

  parser_api:
    build:
      context: ./lab_3
    container_name: parser_api
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - "8001:8000"
    depends_on:
      - postgres
    env_file: .env
```

4. Добавили Celery приложение и настроили его для работы с redis:

```python
import asyncio
from celery import Celery
from parser import parse_and_save

celery_app = Celery("worker", broker="redis://redis:6379/0")


@celery_app.task
def parse_and_save_task(url: str):
    return asyncio.run(parse_and_save(url))
```

5. Добавли эндпонит в fastapi приложении lab_3, который отправляет задачи в очередь:

```python
@app.post("/parse/queue")
async def parse_queue(url: str):
    parse_and_save_task.delay(url)
    return {"message": "Task added to queue."}

```

6. Обновленный docker-compose - с celery воркером и redis:

```yml
services:
  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "6543:5432"
    volumes:
      - ./postgres_data:/var/lib/postgresql/data

  lab_1:
    build:
      context: ../lab_1
      dockerfile: Dockerfile
    restart: always
    container_name: lab_1
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    env_file: .env

  redis:
    image: redis:7
    container_name: redis
    restart: always
    ports:
      - "6379:6379"

  parser_worker:
    build:
      context: ./lab_3
      dockerfile: Dockerfile
    container_name: parser_worker
    env_file: .env
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - postgres
      - redis

  parser_api:
    build:
      context: ./lab_3
      dockerfile: Dockerfile
    container_name: parser_api
    env_file: .env
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    ports:
      - "8001:8000"
    depends_on:
      - postgres
      - redis
```

## Вывод

Написали следующий функционал:

fast_api приложение parser_api, которое парсит книги и отправляет POST запрос на lab1 который сохраняет их в БД. Есть 2 варианта выполнения:

1. /parse/ - синхронный режим, мы сразу же парсим книги, ждем, когда они спасрятся и возращаем, что все ок (или не ок)

2. /parse/queue/ - асинхронный режим, создается задача, которая передается в очередь. Воркеры celery выполяют их. Пользователю отпраляется ответ - задача добавлена в очередь. Воркер ее выполнит, когда сможет.

Все это располагается в контейнерах и управляется через docker compose. 