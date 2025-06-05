from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from pydantic import BaseModel

from ..schemas.user_security_schemas import Token, RefreshToken
from ...db import get_session
from ...models import User
from .user_security import (
    authenticate_user, create_access_token,
    create_refresh_token, validate_token, get_current_user
)

router = APIRouter(
    prefix="/login",
    tags=["Login"],
    responses={401: {"description": "Unauthorized"}}
)


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


@router.post("/", response_model=Token)
async def login_user(
        login_data: LoginRequest,
        session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(session, login_data.username_or_email, login_data.password)

    if not user:
        result = await session.execute(select(User).where(User.email == login_data.username_or_email))
        email_user = result.scalar_one_or_none()

        if email_user:
            user = await authenticate_user(session, email_user.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(
        data={"sub": user.username, "fresh": True},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
        refresh_token_data: RefreshToken,
        session: AsyncSession = Depends(get_session)
):
    try:
        user = await validate_token(token=refresh_token_data.refresh_token, session=session)
        access_token_expires = timedelta(minutes=30)
        refresh_token_expires = timedelta(days=7)

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": user.username},
            expires_delta=refresh_token_expires
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenValidation(BaseModel):
    token: str


@router.post("/validate", response_model=dict)
async def validate_token_endpoint(
        token_data: TokenValidation,
        session: AsyncSession = Depends(get_session)
):
    try:
        user = await validate_token(token=token_data.token, session=session)
        return {
            "valid": True,
            "username": user.username,
            "user_id": user.user_id
        }
    except HTTPException:
        return {
            "valid": False
        }
