## Задание

Необходимо добавить в FastAPI приложение ендпоинт, который будет принимать запросы с URL для парсинга от клиента, отправлять запрос парсеру (запущенному в отдельном контейнере) и возвращать ответ с результатом клиенту.

## Решение

```python
from collections.abc import AsyncGenerator
from typing import Annotated

import aiohttp
import fastapi

from todo_app import settings, tasks
from todo_app.schemas import parser as parser_schemas

router = fastapi.APIRouter(prefix="/parser")


async def get_session() -> AsyncGenerator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


@router.post("/parse", response_model=parser_schemas.ParseUrlResponse)
async def parse(
    parse_request: parser_schemas.ParseUrlRequest,
    session: Annotated[aiohttp.ClientSession, fastapi.Depends(get_session)],
):
    try:
        async with session.post(
            url=settings.settings.parser_url,
            json=parse_request.model_dump(),
        ) as response:
            response.raise_for_status()
            json = await response.json()
    except Exception as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return parser_schemas.ParseUrlResponse.model_validate(json)
```
