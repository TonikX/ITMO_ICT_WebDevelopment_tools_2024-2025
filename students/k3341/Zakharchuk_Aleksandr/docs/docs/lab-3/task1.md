## Задание

1. Реализуйте возможность вызова парсера по http Для этого можно сделать отдельное приложение FastAPI для парсера или воспользоваться библиотекой socket или подобными.

2. Необходимо создать Dockerfile для упаковки FastAPI приложения и приложения с парсером. В Dockerfile указать базовый образ, установить необходимые зависимости, скопировать исходные файлы в контейнер и определить команду для запуска приложения.

3. Необходимо написать docker-compose.yml для управления оркестром сервисов, включающих FastAPI приложение, базу данных и парсер данных. Определите сервисы, укажите порты и зависимости между сервисами.

## Решение

### №1

#### main

```python
from typing import Annotated

import aiohttp
import fastapi
import uvicorn

from web_parser import models, utils

app = fastapi.FastAPI()


@app.post("/parse", response_model=models.ParseUrlResponse)
async def parse(
    parse_request: models.ParseUrlRequest,
    session: Annotated[aiohttp.ClientSession, fastapi.Depends(utils.get_session)],
):
    try:
        result = await utils.get_url_heading(url=str(parse_request.url), session=session)
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return models.ParseUrlResponse(
        url=parse_request.url,
        result=result,
    )


def main():
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
```

#### models

```python
import pydantic


class ParseUrlRequest(pydantic.BaseModel):
    url: pydantic.HttpUrl


class ParseUrlResponse(pydantic.BaseModel):
    url: pydantic.HttpUrl
    result: str
```

#### utils

```python
import asyncio
from collections.abc import AsyncGenerator

import aiohttp
import bs4
import fastapi


async def get_session() -> AsyncGenerator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


async def get_url_heading(url: str, session: aiohttp.ClientSession) -> str:
    # sleep to simulate long operation
    await asyncio.sleep(15)

    async with session.get(url) as response:
        if response.status != fastapi.status.HTTP_200_OK:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Request to {url} failed with status {response.status}",
            )
        
        html = await response.text()
        soup = bs4.BeautifulSoup(html, "lxml")
        title = soup.find("title")

        if not title:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=f"No title found at page {url}",
            )

        return title.text.strip()
```

### №2

#### Todo app

```dockerfile
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry --version

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 8000

ENTRYPOINT [ "./entrypoint.sh" ]

```

**Entrypoint script:**

```sh
#!/bin/sh

set -e

echo "Running migrations..."
poetry run aerich upgrade

echo "Starting application..."
exec poetry run todo_app

```

#### Web parser

```dockerfile
FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry --version

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 8000

CMD ["poetry", "run", "parser"]

```

### №3

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-todos}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    expose:
      - 5432
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-todos}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  todo_app:
    build:
      context: ./todo-app
      dockerfile: Dockerfile
    environment:
      DATABASE_USER: ${POSTGRES_USER:-postgres}
      DATABASE_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      DATABASE_NAME: ${POSTGERS_DB:-todos}
      SERVER_PORT: 8000
      PARSER_HOST: "web_parser"
      PARSER_PORT: 8000
      REDIS_HOST: "redis"
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD:-redispass}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      web_parser:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped

  web_parser:
    build:
      context: ./web-parser
      dockerfile: Dockerfile
    expose:
      - 8000
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge

```
