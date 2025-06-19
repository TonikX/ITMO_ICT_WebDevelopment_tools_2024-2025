from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.connections import get_session
from app.core.security import hash_password
from sqlmodel import Session
from celery.result import AsyncResult
from app.celery_config import celery_app  # подключи Celery app
import httpx
import random

router = APIRouter(prefix="/parser", tags=["parser"])

@router.get("/")
async def proxy_to_parser(url: str, session: Session = Depends(get_session)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://parser-app:8000/parse", params={"url": url})
            response.raise_for_status()
            username = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Parser error: {str(e)}")

    parsed_user = User(
        username=username,
        email=f"{username}{random.randint(1, 1000)}@mail.ru",
        password="1111",
        hashed_password=hash_password("1111")
    )
    session.add(parsed_user)
    session.commit()
    session.refresh(parsed_user)
    return parsed_user

@router.post("/async-parse")
async def async_parse(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://parser-app:8000/celery-parse",
            json={"url": url}
        )
    return {"status": "started", "task_id": response.json().get("task_id")}


@router.get("/result/{task_id}")
def get_celery_result(task_id: str, session: Session = Depends(get_session)):
    result = AsyncResult(task_id, app=celery_app)
    print("Task ready?", result.ready())
    print("Task state:", result.state)
    if result.ready():
        if result.successful():
            username = result.get()
            user = User(
                username=username,
                email=f"{username}{random.randint(1, 1000)}@mail.ru",
                password="1111",
                hashed_password=hash_password("1111")
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return {"status": "success", "user": user}
        else:
            return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": "pending"}