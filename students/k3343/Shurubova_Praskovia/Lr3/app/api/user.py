from starlette.requests import Request
from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import create_access_token,  get_current_user
from app.utils.security import verify_password, hash_password
from fastapi.security import HTTPBearer
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import UserDefault, User, LoginRequest, PasswordChangeRequest, UserUpdate

router = APIRouter()
security = HTTPBearer()


@router.post("/register")
async def register(user: UserDefault, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        password=hash_password(user.password),
        username=user.username,
        full_name=user.full_name,
        bio=user.bio,
        skills=user.skills,
        preferences=user.preferences
    )
    session.add(new_user)
    session.commit()
    return {"message": "User created"}


@router.post("/login")
async def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me(request: Request, session: Session = Depends(get_session)):
    payload = get_current_user(request)
    user = session.get(User, int(payload["id"]))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/change-password")
async def change_password(
        data: PasswordChangeRequest,
        request: Request,
        session: Session = Depends(get_session)
):
    payload = get_current_user(request)
    user = session.get(User, int(payload["id"]))

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    user.password = hash_password(data.new_password)
    session.commit()
    return {"message": "Password updated"}


@router.get("/")
async def list_users(request: Request, session: Session = Depends(get_session)):
    get_current_user(request)
    return session.exec(select(User)).all()


@router.get("/{user_id}")
def user_by_id(user_id: int, session: Session = Depends(get_session)) -> User:
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/update/{user_id}")
def user_update(user_id: int, user: UserUpdate, session: Session = Depends(get_session)) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)

    for key, value in user_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/delete/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted"}

