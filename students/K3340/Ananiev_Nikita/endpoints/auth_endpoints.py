import os
import hashlib

from base64 import b64encode
from fastapi import APIRouter, HTTPException, Depends
from models.models import Profile
from models.default_models import ProfileDefault, AuthModel
from sqlmodel import select
from connection import get_session
from typing_extensions import TypedDict
from jwt_logic import JWTAuth
from dotenv import load_dotenv

load_dotenv()

jwt_secret = os.getenv("JWT_SECRET_KEY")
auth_router = APIRouter()
auth_checker = JWTAuth(jwt_secret)

def get_password_hash(password: str) -> bytes:
    hashed = hashlib.sha256(password.encode()).digest()
    return b64encode(hashed)

@auth_router.post('/login')
async def login(profile: AuthModel, session = Depends(get_session)) -> TypedDict('Response', {"status": int, "jwt_token": str}):
    found = session.exec(select(Profile).where(Profile.email == profile.email)).first()
    if not found:
        raise HTTPException(status_code=404, detail="User not found")
    password_hash = get_password_hash(profile.password)
    if found.password != password_hash.decode():
        raise HTTPException(status_code=401, detail="Incorrect password")
    token = auth_checker.encode_token(found.id)
    return {"status": 200, "jwt_token": token}


@auth_router.post('/register')
async def register(profile: ProfileDefault, session = Depends(get_session)) -> TypedDict('Response', {"status": int, "created": Profile}):
    profile = Profile.model_validate(profile)
    found = session.exec(select(Profile).where(Profile.email == profile.email)).first()
    if found:
        raise HTTPException(status_code=409, detail="Email already registered")
    password_hash = get_password_hash(profile.password)
    profile.password = password_hash.decode()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return {"status": 201, "created": profile}
