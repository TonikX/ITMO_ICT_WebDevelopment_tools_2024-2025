from datetime import datetime
from http.client import HTTPException
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from asyncio_parse import async_parse
from multi_parse import multi_parse
from thread_parse import thread_parse

app = FastAPI()





class ParseRequest(BaseModel):
    urls: List[str]

@app.post("/async-parse")
async def parse_async(urls: list[str]):
    if not urls:
        raise HTTPException(status_code=400, detail="Не передано ни одного URL")

    start_time = datetime.now()

    try:
        result = await async_parse(urls)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "status": "Завершено",
            "processed_urls": urls,
            "result": result,
            "execution_time_seconds": round(duration, 2)
        }
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при парсинге: {str(e)}, время выполнения: {round(duration, 2)} сек."
        )

@app.post("/multi-parse")
def parse_multi(urls: List[str]):
    if not urls:
        raise HTTPException(status_code=400, detail="Не передано ни одного URL")

    start_time = datetime.now()

    try:
        multi_parse(urls)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "status": "Завершено",
            "processed_urls": urls,
            "execution_time_seconds": round(duration, 2)
        }
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при парсинге: {str(e)}, время выполнения: {round(duration, 2)} сек."
        )

@app.post("/thread-parse")
def parse_thread(urls: List[str]):
    if not urls:
        raise HTTPException(status_code=400, detail="Не передано ни одного URL")

    start_time = datetime.now()

    try:
        thread_parse(urls)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "status": "Завершено",
            "processed_urls": urls,
            "execution_time_seconds": round(duration, 2)
        }
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при парсинге: {str(e)}, время выполнения: {round(duration, 2)} сек."
        )