from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlmodel import Session

from db.connection import get_session
from auth.utils import decode_access_token, auth_scheme
from middleware.admin import get_current_admin
from middleware.user import get_user_permission
from services.users_service import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user,
    login_user,
    register_user,
    change_password,
)
from models.models import Account, AccountUpdate

router = APIRouter(tags=["Users"], prefix="/users")


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


@router.get("/", response_model_exclude={"password"})
async def list_users(
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> list[Account]:
    return get_all_users(session)


@router.get("/me", response_model_exclude={"password"})
async def get_me(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> Account:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}", response_model_exclude={"password"})
async def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Account:
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/new", response_model_exclude={"password"})
async def create_new_user(
    user: Account,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    admin: Account = Depends(get_current_admin),
) -> Account:
    return create_user(session, user)


@router.put("/{user_id}", response_model_exclude={"password"})
async def update_existing_user(
    user_id: int,
    user_update: AccountUpdate,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    _: None = Depends(get_user_permission),
) -> Account:
    update_fields = user_update.dict(exclude_unset=True)
    updated = update_user(session, user_id, update_fields)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated


@router.delete("/{user_id}", response_model_exclude={"password"})
async def delete_existing_user(
    user_id: int,
    session: Session = Depends(get_session),
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    _: None = Depends(get_user_permission),
) -> Account:
    deleted = delete_user(session, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted


@router.post("/login", response_model_exclude={"password"})
async def login(username: str, password: str, session: Session = Depends(get_session)) -> str:
    token = login_user(session, username, password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token


@router.post("/register", response_model_exclude={"password"})
async def register(user: Account, session: Session = Depends(get_session)) -> Account:
    user.role = "user"
    user = register_user(session, user)
    if not user:
        raise HTTPException(status_code=400, detail="User already exists")
    return user


@router.post("/change-password")
async def update_password(
    password_data: PasswordChange,
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
    session: Session = Depends(get_session),
) -> dict:
    payload = decode_access_token(token.credentials)
    if "error" in payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    success = change_password(session, user_id, password_data.old_password, password_data.new_password)

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Password change failed. Check your current password.",
        )

    return {"message": "Password changed successfully"}
