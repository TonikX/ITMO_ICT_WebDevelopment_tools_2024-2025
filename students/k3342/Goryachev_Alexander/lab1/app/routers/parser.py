from fastapi import APIRouter, Depends, HTTPException
from app.models import User
import httpx
from app.connections import get_session
from app.core.security import verify_password, hash_password
from sqlmodel import Session, select

import random
router = APIRouter(prefix="/parser", tags=["parser"])

@router.get("/")
async def proxy_to_parser(url: str, session: Session = Depends(get_session)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://parser-app:8000/parse", params={"url": url})
            response.raise_for_status()
            username =  response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Parser error: {str(e)}")
    parsed_user = User(username = username, email = username+str(random.randint(1,1000))+"@mail.ru", password = "1111", hashed_password=hash_password("1111"))
    session.add(parsed_user)
    session.commit()
    session.refresh(parsed_user)
    return parsed_user

@router.post("/async-parse")
async def async_parse(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://parser-app:8000/celery-parse", json={"url": url})
    return {"status": "started", "message": response.json()}