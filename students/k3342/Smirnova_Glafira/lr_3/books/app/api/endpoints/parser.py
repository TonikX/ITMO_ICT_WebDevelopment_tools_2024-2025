import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.models import BookParsed

router = APIRouter()

class ParseRequest(BaseModel):
    url: str

@router.post("/parse-queue")
async def parse_url(data: ParseRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://parser:9000/parse", json={"url": data.url})
        response.raise_for_status()
        return {"message": "Парсинг отправлен", "response": response.json()}
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка подключения к парсеру: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка парсера: {e.response.text}")

@router.get("/task-status/{task_id}")
async def proxy_task_status(task_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://parser:9000/task-status/{task_id}")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ошибка при обращении к парсеру: {e}")

@router.get("/parsed-books")
def get_parsed_books(session: Session = Depends(get_session)):
    books = session.exec(select(BookParsed)).all()
    return books

@router.post("/parse-direct")
async def proxy_parse_direct(data: ParseRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://parser:9000/parse-direct", json={"url": data.url})
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка подключения к парсеру: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)