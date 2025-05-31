from fastapi import APIRouter, Depends, HTTPException, Form
from sqlmodel import Session, select
from app.db import get_session
from app.models import User
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/register")
def register_user(username: str, email: str, password: str, session: Session = Depends(get_session)):
    hashed_password = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed_password, role="user")
    session.add(user)
    session.commit()
    return {"message": "User registered successfully"}


@router.post("/login")
def login_user(email: str = Form(...), password: str = Form(...), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
