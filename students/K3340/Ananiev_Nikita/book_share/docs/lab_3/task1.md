## **Подзадача 1**: Упаковка парсера
### Создание отдельного приложения для парсера позволит вызывать его из других приложений
Код нового fastapi-приложения парсера:
```python
import asyncio
import uvicorn
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from database import AsyncDBFiller, BookInfoParsed
from async_parser import worker, books_count, get_books_links, workers_count
from helpers import tpl, base

@asynccontextmanager
async def init_async_connection():
    filler = AsyncDBFiller()
    try:
        await filler.connect()
        yield filler
    finally:
        await filler.disconnect()


async def get_async_connection():
    async with init_async_connection() as conn:
        yield conn

app = FastAPI()

@app.post("/parse")
async def parse(conn: AsyncDBFiller = Depends(get_async_connection)) -> list[BookInfoParsed]:
    result = []
    pages = [base + tpl.format(index) for index in range(1, books_count + 1, 25)]
    all_links = await get_books_links(pages)
    per_worker = books_count // workers_count
    pieces = await asyncio.gather(*[worker(all_links[i:i + per_worker], conn) for i in range(0, books_count, per_worker)])
    for piece in pieces:
        result.extend(piece)
    return result


if __name__ == '__main__':
    uvicorn.run("parser_app:app", host='0.0.0.0', port=4242, reload=True)
```

По сути в эндпоинт перенесена main функция асинхронного парсера из лабораторной работы №2. <br> 
Подключение к базе используется оттуда же, только здесь применен асинхронный менеджер контекста для работы с зависимостями fastapi.

Так выглядит .env для приложения парсера:
```shell
DB_CONN=postgresql://postgres:aventador@db_container/book_share_db
```

Dockerfile парсера:
```dockerfile
FROM python:3.11-slim

WORKDIR /parser

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

COPY parser.env .env

EXPOSE 4242

CMD ["uvicorn", "parser_app:app", "--host", "0.0.0.0", "--port", "4242", "--reload"]
```