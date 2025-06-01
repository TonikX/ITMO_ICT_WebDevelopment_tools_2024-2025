import aiohttp
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from starlette.responses import JSONResponse
from starlette.status import HTTP_201_CREATED
from typing_extensions import List

from app.celery_app import celery_app
from auth.auth import AuthHandler
from model.models.models import User
from model.schemas.parse import ParseRequest
from model.schemas.user import UserCreate, UserLogin, UserFullRead, UserPasswordChange
from db.connection import get_session
from repos.user_repos import select_all_users, find_user

user_router = APIRouter()
auth_handler = AuthHandler()


@user_router.post("/parse")
async def parse(parse_request: ParseRequest):
    parser_url = "http://parser_app:8001/parse"
    async with aiohttp.ClientSession() as client:
        response = await client.post(parser_url, json=parse_request.model_dump(), timeout=15)
        response.raise_for_status()
        return await response.json()


@user_router.post("/parse-queue")
def start_parse(request: ParseRequest):
    task = celery_app.send_task("app.tasks.parse_url_task", args=[request.url])
    return {"task_id": task.id}


@user_router.get("/status/{task_id}")
def check_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {"status": result.status, "result": result.result}


@user_router.post('/registration', status_code=201, tags=['users'],
                  description='Register new user')
def register(user: UserCreate, session=Depends(get_session)):
    users = select_all_users()
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail='Email is taken')
    hashed_pwd = auth_handler.get_password_hash(user.password)
    u = User(email=user.email, password=hashed_pwd, name=user.name, bio=user.bio)
    session.add(u)
    session.commit()
    return JSONResponse(status_code=HTTP_201_CREATED, content={"Message": "User Registered"})


@user_router.post('/login', tags=['users'])
def login(user: UserLogin):
    user_found = find_user(user.email)
    if not user_found:
        raise HTTPException(status_code=401, detail='Invalid email and/or password')
    verified = auth_handler.verify_password(user.password, user_found.password)
    if not verified:
        raise HTTPException(status_code=401, detail='Invalid email and/or password')
    token = auth_handler.encode_token(user_found.email)
    return {'token': token}


@user_router.get('/users/profile', tags=['users'])
def profile(user: User = Depends(auth_handler.get_current_user)):
    return user


@user_router.get("/users", response_model=List[UserFullRead], tags=['users'])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()


@user_router.post("/password", tags=['users'])
def change_password(
        data: UserPasswordChange,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_handler.get_current_user)
):
    if not auth_handler.verify_password(data.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    current_user.password = auth_handler.get_password_hash(data.new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password updated successfully"}
