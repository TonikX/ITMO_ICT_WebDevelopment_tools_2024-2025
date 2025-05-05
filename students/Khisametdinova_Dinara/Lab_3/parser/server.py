from fastapi import FastAPI, HTTPException

import aiohttp, asyncio

from dtos import ParseRequest
from parser import parse_and_save_async
from tasks import run_parsing_task

app = FastAPI()

@app.post("/parse")
async def parse_url(req: ParseRequest):
    try:
        async with aiohttp.ClientSession() as session:
            await parse_and_save_async(session, req.url, req.table_name)
        return {"message": f"Parsed {req.url} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/enqueue-parse")
def enqueue_parse(req: ParseRequest):
    run_parsing_task.delay(req.dict())
    return {"message": f"Task enqueued for {req.url}"}