from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from schemas import UserCreate, UserRead, Token, TokenData, PasswordChange
from models import User
from connection import get_session
from security import hash_pwd, verify_pwd, create_access_token, decode_token
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_by_name(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def authenticate(session: Session, username: str, password: str) -> User | None:
    user = get_user_by_name(session, username)
    if user and verify_pwd(password, user.hashed_password):
        return user


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_name(session, payload.username):
        raise HTTPException(400, "username taken")
    u = User(username=payload.username,
             hashed_password=hash_pwd(payload.password))
    session.add(u)
    session.commit(); session.refresh(u)
    return u


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(get_session)):
    user = authenticate(session, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid creds")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme),
                     session: Session = Depends(get_session)) -> User:
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        assert username
    except (JWTError, AssertionError):
        raise HTTPException(401, "Could not validate credentials")
    user = get_user_by_name(session, username)
    if not user:
        raise HTTPException(401, "User not found")
    return user


@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return current


@router.get("/users", response_model=list[UserRead])
def list_users(session: Session = Depends(get_session),
               _: User = Depends(get_current_user)):
    return session.exec(select(User)).all()


@router.post("/change-password", status_code=204)
def change_password(data: PasswordChange,
                    current: User = Depends(get_current_user),
                    session: Session = Depends(get_session)):
    if not verify_pwd(data.old_password, current.hashed_password):
        raise HTTPException(400, "old password incorrect")
    current.hashed_password = hash_pwd(data.new_password)
    session.add(current); session.commit()
