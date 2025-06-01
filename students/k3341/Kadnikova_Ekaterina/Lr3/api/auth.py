from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from models.user import User
from schemas.user import UserCreate, UserRead, UserLogin
from connection import get_session
from authorization.hash_service import hash_password, verify_password
from authorization.jwt_generator import verify_access_token, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserRead)
async def register(user_create: UserCreate, db: Session = Depends(get_session)):
    db_user_by_email = db.query(User).filter(User.email == user_create.email).first()
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_by_username = db.query(User).filter(User.username == user_create.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(user_create.password)

    user = User(**user_create.dict(), password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login")
async def login(user_base: UserLogin, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == user_base.username).first()

    if not user or not verify_password(user_base.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token, credentials_exception)

    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None or user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user

@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/users/{user_id}/change-password")
async def change_password(user_id: int, new_password: str, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)

    return {"msg": "Password updated successfully"}
