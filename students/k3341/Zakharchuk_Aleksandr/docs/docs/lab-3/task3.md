## Задание

1. Необходимо добавить зависимости для Celery и Redis в проект. Celery будет использоваться для обработки задач в фоне, а Redis будет выступать в роли брокера задач и хранилища результатов.

2. Необходимо создать файл конфигурации для Celery. Определть задачу для парсинга URL, которая будет выполняться в фоновом режиме.

3. Необходимо добавить сервисы для Redis и Celery worker в docker-compose.yml. Определите зависимости между сервисами, чтобы обеспечить корректную работу оркестра.

4. Необходимо добавить в FastAPI приложение маршрут для асинхронного вызова парсера. Маршрут должен принимать запросы с URL для парсинга, ставить задачу в очередь с помощью Celery и возвращать ответ о начале выполнения задачи.

## Решение

### №1

```toml
[tool.poetry.dependencies]
# ...
celery = "^5.5.2"
redis = "^6.1.0"
# ...
```

### №2

```python
import celery
import requests

from todo_app import settings
from todo_app.schemas import parser as parser_schemas

celery_app = celery.Celery(
    __name__,
    broker=settings.settings.redis_url,
    backend=settings.settings.redis_url,
)

@celery_app.task
def parse_url(parse_request: str) -> str:
    try:
        response = requests.post(url=settings.settings.parser_url, data=parse_request)
        response.raise_for_status()
        json = response.json()
    except Exception as err:
        return str(err)

    return json.get("result", "error")

```

### №3

```yaml
services:
  # ...
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD:-redispass}
    expose:
      - 6379
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

  celery_worker:
    build:
      context: ./todo-app
      dockerfile: Dockerfile.celery_worker
    environment:
      PARSER_HOST: "web_parser"
      PARSER_PORT: 8000
      REDIS_HOST: "redis"
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD:-redispass}
    depends_on:
      redis:
        condition: service_healthy
      todo_app:
        condition: service_started
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### №4

```python
from collections.abc import AsyncGenerator
from typing import Annotated

import aiohttp
import celery
import celery.result
import fastapi

from todo_app import settings, tasks
from todo_app.schemas import parser as parser_schemas

router = fastapi.APIRouter(prefix="/parser")

# ...

@router.post("/parse/start", response_model=parser_schemas.ParserTaskResponse)
async def parse(parse_request: parser_schemas.ParseUrlRequest):
    task = tasks.parse_url.delay(parse_request.model_dump_json())
    return parser_schemas.ParserTaskResponse(id=task.id, state="STARTED")


@router.get("/parse/result/{task_id}", response_model=parser_schemas.ParserTaskResponse)
async def parse(task_id: str):
    result = celery.result.AsyncResult(task_id)

    if result.state == "FAILURE":
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(result.result),
        )
    
    if result.state == "SUCCESS":
        return parser_schemas.ParserTaskResponse(
            id=task_id,
            state=result.state,
            result=result.result,
        )

    return parser_schemas.ParserTaskResponse(
        id=task_id,
        state=result.state,
    )

```
