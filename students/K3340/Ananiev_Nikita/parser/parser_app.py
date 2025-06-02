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
