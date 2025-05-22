from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import Token, UserCreate, UserInDB
from app.services.user import user_service
from app.services.auth import create_user_token
from app.api.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await user_service.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await create_user_token(user.username)

@router.post("/register", response_model=UserInDB)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await user_service.get_by_username(db, user_in.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    return await user_service.create_user(db, user_in)