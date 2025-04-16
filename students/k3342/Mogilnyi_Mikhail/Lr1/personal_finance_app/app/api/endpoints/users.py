from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from datetime import timedelta
from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.auth.hash import get_password_hash, verify_password
from app.auth.jwt import create_access_token

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token = create_access_token({"sub": db_user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
