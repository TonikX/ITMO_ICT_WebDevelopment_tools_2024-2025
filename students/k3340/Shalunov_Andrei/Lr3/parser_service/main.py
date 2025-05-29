import os
import time
import asyncio
from typing import List
from aiohttp import ClientSession
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from parser import tpl, base, parse_book_links, parse_book_details
from db import AsyncDBFiller

DB_CONN = os.getenv("DATABASE_URL")

WORKERS = 4
BOOKS_TOTAL = 100

app = FastAPI()

class ParseRequest(BaseModel):
    url: str

@app.post("/parse")
async def parse_endpoint(req: ParseRequest):
    filler = AsyncDBFiller(dsn=DB_CONN)
    await filler.connect()
    try:
        async with ClientSession() as session:
            resp = await session.get(req.url)
            html = await resp.text()
            details = parse_book_details(html)
            await filler.add_book(details, source="async")
        return {"message": "Parsing completed", "url": req.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await filler.disconnect()

@app.post("/parse-all")
async def parse_all():
    filler = AsyncDBFiller(dsn=DB_CONN)
    await filler.connect()
    try:
        async with ClientSession() as session:
            pages = [base + tpl.format(i) for i in range(1, BOOKS_TOTAL+1, 25)]
            tasks = [session.get(url) for url in pages]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            links = []
            for r in results:
                if not isinstance(r, Exception):
                    html = await r.text()
                    links.extend(parse_book_links(html))
                    await r.release()

            per = (len(links) + WORKERS - 1) // WORKERS
            chunks = [links[i:i+per] for i in range(0, len(links), per)]
            workers = [
                worker(chunk, session, filler)
                for chunk in chunks
            ]
            saved_counts: List[int] = await asyncio.gather(*workers)
        return {"saved_total": sum(saved_counts)}
    finally:
        await filler.disconnect()

async def worker(chunk: List[str], session: ClientSession, filler: AsyncDBFiller) -> int:
    saved = 0
    for url in chunk:
        try:
            resp = await session.get(url)
            html = await resp.text()
            details = parse_book_details(html)
            if await filler.add_book(details, source="async"):
                saved += 1
            await resp.release()
        except:
            continue
    return saved