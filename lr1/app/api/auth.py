from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models
from app.schemas import auth as auth_schema 
from app.crud import auth as auth_crud
from app.database import SessionLocal
from app.core import security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=auth_schema.UserOut)
def register(user: auth_schema.UserCreate, db: Session = Depends(get_db)) -> auth_schema.UserOut:
    db_user = auth_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = auth_crud.create_user(db, user=user)
    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = auth_crud.get_user_by_username(db, username=form_data.username)
    if not db_user or not security.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = security.generate_jwt({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login")), 
                     db: Session = Depends(get_db)) -> models.User:
    payload = security.verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/users/me", response_model=auth_schema.UserOut)
def read_current_user(current_user: models.User = Depends(get_current_user)) -> auth_schema.UserOut:
    return current_user


@router.get("/users", response_model=list[auth_schema.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[auth_schema.UserOut]:
    users = auth_crud.get_users(db, skip=skip, limit=limit)
    return users


@router.post("/change-password")
def change_password(change: auth_schema.ChangePassword, 
                    current_user: models.User = Depends(get_current_user), 
                    db: Session = Depends(get_db)):
    if not security.verify_password(change.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    auth_crud.update_password(db, current_user, change.new_password)
    return {"msg": "Password updated successfully"}
