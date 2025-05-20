import httpx
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/parse_books", tags=["Parser"])


@router.post("/sync-parse")
async def start_parse():
    parser_url = "http://parser:8001/parse"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(parser_url)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка связи с парсером: {e}")


@router.post("/async-parse")
async def async_parse():
    response = requests.post("http://parser:8001/celery-trigger")
    return {"status": "task sent", "details": response.json()}


@router.get("/async-status/{task_id}")
async def check_async_status(task_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://parser:8001/task-status/{task_id}")
        return response.json()
