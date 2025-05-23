from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel import Session

import app.schemas as schemas
import app.crud as crud
from app.database import get_session
from app.core.jwt import decode_access_token, ReusableOAuth2
from app.models.models import Profile

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.ProfileRead)
def register(reg: schemas.Register, db: Session = Depends(get_session)):
    if crud.get_profile_by_email(db, reg.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    return crud.create_profile(db, reg)

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    prof = crud.authenticate_profile(db, form_data.username, form_data.password)
    if not prof:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = crud.create_access_token_for_user(prof)
    return {"access_token": token, "token_type": "bearer"}

def get_token_data(token: str = Security(ReusableOAuth2)) -> schemas.TokenData:
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing token")
    return schemas.TokenData(user_id=int(payload["user_id"]))

def get_current_user(token_data: schemas.TokenData = Depends(get_token_data), db: Session = Depends(get_session)) -> Profile:
    user = db.get(Profile, token_data.user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user

def authenticate_request(user: Profile = Depends(get_current_user)) -> Profile:
    return user