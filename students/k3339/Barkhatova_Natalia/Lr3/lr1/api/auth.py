from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_session
from models import User as UserModel
from schemas.user import User as UserSchema, UserCreate, UserLogin
from security.token_service import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(UserModel).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    data = user.dict()
    data['password'] = get_password_hash(user.password)
    db_user = UserModel(**data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/login")
def login(form_data: UserLogin, session: Session = Depends(get_session)):
    user = session.query(UserModel).filter_by(email=form_data.email).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
