import os
import hashlib
from base64 import b64encode
from fastapi import APIRouter, HTTPException, Depends
from models.models import Profile
from models.default_models import ProfileDefault
from sqlmodel import select
from connection import get_session
from typing_extensions import TypedDict
from jwt_logic import JWTAuth
from dotenv import load_dotenv

load_dotenv()
jwt_secret = os.getenv("JWT_SECRET_KEY")
auth_checker = JWTAuth(jwt_secret)
auth_router = APIRouter()

def get_encoded_password(password: str) -> str:
    hashed = hashlib.sha256(password.encode()).digest()
    return b64encode(hashed).decode()

@auth_router.post("/register")
async def register(profile: ProfileDefault, session=Depends(get_session)) -> TypedDict("Response", {"status": int, "created": Profile}):
    if session.exec(select(Profile).where(Profile.email == profile.email)).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    profile.password = get_encoded_password(profile.password)
    db_profile = Profile.model_validate(profile)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return {"status": 201, "created": db_profile}

@auth_router.post("/login")
async def login(profile: ProfileDefault, session=Depends(get_session)) -> TypedDict("Response", {"status": int, "jwt_token": str}):
    found = session.exec(select(Profile).where(Profile.email == profile.email)).first()
    if not found or found.password != get_encoded_password(profile.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_checker.encode_token(found.id)
    return {"status": 200, "jwt_token": token}
