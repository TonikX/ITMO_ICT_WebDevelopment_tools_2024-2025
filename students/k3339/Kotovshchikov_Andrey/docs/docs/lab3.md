# Лабораторная работа 3: Упаковка FastAPI приложения в Docker, Работа с источниками данных и Очереди

[Ссылка](https://github.com/KotovshchikovAndrey/ITMO_ICT_WebDevelopment_tools_2024-2025/tree/lab3/students/k3339/Kotovshchikov_Andrey/Lab3)

## Вызов парсера из FastAPI

Перед тем как поднимать всю инфраструктуру в Docker / docker-compose необходимо реализовать возможность
вызова парсера через API. Для этого на стороне парсера были реализован HTTP энпоинт при помощи FastApi.

```python
@app.post("/parse", status_code=status.HTTP_200_OK)
async def parse(url: str):
    await parse_and_save(url)
    return {"message": "ok"}
```

В этом коде мы принимаем ссылку (url) на ресурс, который необходимо спарсить и вызываем асинхронный парсер из предыдущей лабораторной работы (на asyncio). В конце - возвращаем статус 200 и сообщение что запрос прошел успешно.

Так как парсер является внутренним ресурсом, доступ к которому снаружи (вне Docker контейнера) будет ограничен, запросы к парсеру будут осуществляться через приложение из лабораторной работы 1, в которое был внедрен функционал для взаимодействия с парсером.

```python
@router.post("/", status_code=status.HTTP_200_OK)
async def parse(
    service: Annotated[ParserService, Depends(get_parser_service)],
    dto: ParseUrlDTO,
    async_parse: bool = False,
):
    await service.parse(dto, is_async=async_parse)
    return {"message": "ok"}
```

```python
class ParserService:
    async def parse(self, dto: ParseUrlDTO, is_async: bool = False) -> None:
        try:
            async with httpx.AsyncClient(base_url=settings.PARSER_URL) as client:
                url = "/parse" if not is_async else "/parse/async"
                response = await client.post(url, params=dto.model_dump(mode="json"))
                if not response.is_success:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Parser not available",
                    )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Parser not available",
            )
```

Здесь контроллер вызывает метод parse у ParserService, который отправляет запрос парсеру с переданым в теле запроса url и тем самым запускает его. Параметр is_async нужен для асинхронного (отложенного) запуска парсера, который далее будет реализован при помощи **Celery**.

## Вызов парсера из FastAPI через очередь

Процесс парсинга может быть довольно долгим. Поэтому, чтобы не заставлять клиента ждать, мы можем отправлять задачу на парсинг в очередь и сразу вернуть клиенту сообщение со статусом 200. Такой функционал был реализован при помощи очереди **Celery**.

```python
import os
import logging

import psycopg
import requests
from bs4 import BeautifulSoup
from celery import Celery
from parser.logger import setup_logger

logger = logging.getLogger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379")


@celery.task(name="parse")
def parse_and_save_async(url: str) -> None:
    setup_logger()

    connection = psycopg.connect(os.getenv("POSTGRES_URL"))
    cursor = connection.cursor()
    logger.info("Connected to database")

    skills: set[str] = set()
    logger.info("Start parse: %s", url)
    response = requests.get(url)
    if response.status_code != 200:
        logger.error("Parse failed: %s", url)
        return

    soup = BeautifulSoup(response.text, features="html.parser")
    title = soup.find("title").text
    logger.info("Page title: %s", title)

    for row in soup.find("table").find("tbody").find_all("tr"):
        skill = row.get_text().split()[1]
        skills.add(skill)

    query = """INSERT INTO skill VALUES (DEFAULT, %s)
        ON CONFLICT (name) DO NOTHING;"""

    cursor.executemany(query, map(lambda skill: (skill,), skills))
    connection.commit()
    logger.info("Skills saved")

    connection.close()
    logger.info("End parse: %s", url)
```

Также на уровне парсера был добавлен еще один эндпоинт для запуска задачи в отложенном режиме при помощи **Celery**.

```python
@app.post("/parse/async", status_code=status.HTTP_200_OK)
async def parse(url: str):
    parse_and_save_async.delay(url)
    return {"message": "ok"}
```

## Упаковка FastAPI приложения, базы данных и парсера данных в Docker

И наконец, когда приложение полностью готово, его необходимо упаковать в Docker. Для создания образа приложения и парсера был создан единый Docker файл с аргументом **PROJECT**, через который в docker-compose мы укажем какой из проектов мы хотим сбилдить (парсер или app). Помимо прочего в качестве лучшей практики был применен подход **multistage** для минимизации размера итогового образа.

```Dockerfile
FROM python:3.13-slim AS build

ARG PROJECT=app

WORKDIR /${PROJECT}

COPY ./${PROJECT}/poetry.lock ./${PROJECT}/pyproject.toml /${PROJECT}

RUN apt-get update && \
    apt-get install \
    -y libpq-dev gcc && \
    pip install --upgrade pip && \
    pip install --upgrade wheel && \
    pip install poetry --no-cache-dir && \
    poetry self add poetry-plugin-export && \
    poetry export -o requirements.txt && \
    pip wheel \
    --no-deps \
    --no-cache-dir \
    --wheel-dir /${PROJECT}/wheels \
    -r requirements.txt


FROM python:3.13-slim AS run

ARG PROJECT=app

WORKDIR /${PROJECT}

COPY --from=build /${PROJECT}/wheels /${PROJECT}/wheels
COPY --from=build /${PROJECT}/requirements.txt .

RUN pip install --upgrade pip && \
    pip install \
    --no-cache-dir \
    --no-deps \
    --no-index \
    --find-links=/${PROJECT}/wheels \
    -r requirements.txt

COPY ./${PROJECT} .

CMD [ "/bin/bash" ]
```

В конце вся инфраструктура была собрана в едином docker-compose файле.

```yml
services:
  postgres:
    image: postgres
    container_name: postgres
    restart: unless-stopped
    expose:
      - 5432
    environment:
      - PGDATA=/var/lib/postgresql/data/postgres
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_DB
    networks:
      - public_net
      - parser_net
    volumes:
      - postgres_data:/var/lib/postgresql/data/postgres

  redis:
    image: redis
    container_name: redis
    restart: unless-stopped
    expose:
      - 6379
    networks:
      - parser_net
    volumes:
      - redis_data:/data

  worker:
    container_name: worker
    command: celery -A parser.tasks.celery worker --loglevel=info
    build:
      context: .
      dockerfile: ./docker/Dockerfile
      args:
        - PROJECT=parser
    restart: unless-stopped
    environment:
      - CELERY_BROKER_URL
      - CELERY_BACKEND_URL
      - POSTGRES_URL
    networks:
      - parser_net
    depends_on:
      - redis

  parser:
    container_name: parser
    command: uvicorn parser.api:app --host 0.0.0.0
    build:
      context: .
      dockerfile: ./docker/Dockerfile
      args:
        - PROJECT=parser
    restart: unless-stopped
    environment:
      - PYTHONPATH=/parser
      - CELERY_BROKER_URL
      - CELERY_BACKEND_URL
      - POSTGRES_URL
    expose:
      - 8000
    networks:
      - public_net
      - parser_net
    depends_on:
      - worker
      - postgres

  app:
    container_name: app
    command: bash -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0"
    build:
      context: .
      dockerfile: ./docker/Dockerfile
      args:
        - PROJECT=app
    restart: unless-stopped
    environment:
      - PYTHONPATH=/app
      - APP_PARSER_URL=http://parser:8000
      - APP_DATABASE_URI
      - APP_JWT_SECRET
    ports:
      - "8000:8000"
    networks:
      - public_net
    depends_on:
      - parser
      - postgres

networks:
  parser_net:
    name: "parser_net"
  public_net:
    name: "public_net"

volumes:
  redis_data:
  postgres_data:
```

Из интересного здесь используются кастомные **networks**. Это сделано для того, чтобы контейнер **app** не имел доступ к **worker** и **redis**, так как они нужны только парсеру, следовательно, не должны быть доступны никому кроме него. Порты всех запущенных контейнеров кроме **app** спрятаны внутри сети Docker, и недоступны снаружи. Для того, чтобы данные не пропали при удалении контейнера были подключены **volumes**, позволяющие связать файлы внутри контейнера с файловой системой хоста.

Для запуска необходимо выполнить:

```bash
docker compose --env-file .env up -d
```

При помощи **docker-cli** можно убедиться что все работает:

```bash
 docker logs -f app
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
