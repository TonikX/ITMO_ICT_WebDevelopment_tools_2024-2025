from fastapi import APIRouter, HTTPException
from celery import Celery
import httpx
from pydantic import BaseModel
import os
from dotenv import load_dotenv

router = APIRouter(prefix="/parse", tags=["Parser"])

PARSER_URL = "http://parser_service:8001/parse"
print("DEBUG PARSER_URL =", PARSER_URL)

celery_app = Celery(
    "parser_celery",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)
class ParseRequest(BaseModel):
    url: str

@router.post("/")
async def call_parser(request: ParseRequest):
    url = request.url
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(PARSER_URL, json={"url": url}) 
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print("httpx.RequestError:", repr(e))
            raise HTTPException(status_code=502, detail=f"Parser service not available: {repr(e)}")

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=response.text)


@router.post("/async-parse")
def enqueue_parse_task(url: str):
    task = celery_app.send_task("parse_from_url", args=[url])  
    return {"task_id": task.id, "status": "queued"}
