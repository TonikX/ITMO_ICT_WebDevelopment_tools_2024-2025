from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import httpx
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import User
from ..users.user_security import get_current_admin_user, get_session

router = APIRouter(prefix="/parser", tags=["parser"])


class ParseRequest(BaseModel):
    urls: List[HttpUrl]
    parser_type: str = "async"  # async, threading, multiprocessing


class ParseResponse(BaseModel):
    task_id: str
    status: str
    message: str
    teams_parsed: Optional[int] = None
    schools_created: Optional[int] = None
    tournaments_created: Optional[int] = None


# URL парсера (в Docker Compose это будет http://parser:8001)
PARSER_URL = "http://parser:8001"


@router.post("/parse", response_model=ParseResponse)
async def start_parsing(
        request: ParseRequest,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user)
):
    """
    Запускает парсинг данных через внешний сервис парсера
    Доступно только администраторам
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PARSER_URL}/parse",
                json=request.dict()
            )
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service unavailable: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Parser service error: {e.response.text}"
        )


@router.get("/status/{task_id}", response_model=ParseResponse)
async def get_parsing_status(
        task_id: str,
        current_user: User = Depends(get_current_admin_user)
):
    """
    Получает статус задачи парсинга
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{PARSER_URL}/status/{task_id}")
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service unavailable: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Parser service error: {e.response.text}"
        )


@router.get("/tasks")
async def list_parsing_tasks(
        current_user: User = Depends(get_current_admin_user)
):
    """
    Получает список всех задач парсинга
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{PARSER_URL}/tasks")
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service unavailable: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Parser service error: {e.response.text}"
        )


@router.delete("/status/{task_id}")
async def delete_parsing_task(
        task_id: str,
        current_user: User = Depends(get_current_admin_user)
):
    """
    Удаляет статус задачи парсинга
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(f"{PARSER_URL}/status/{task_id}")
            response.raise_for_status()
            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service unavailable: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Parser service error: {e.response.text}"
        )


@router.get("/health")
async def check_parser_health():
    """
    Проверяет доступность сервиса парсера
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PARSER_URL}/health")
            response.raise_for_status()
            return {
                "parser_status": "healthy",
                "parser_response": response.json()
            }

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Parser service unavailable: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Parser service unhealthy: {e.response.text}"
        )