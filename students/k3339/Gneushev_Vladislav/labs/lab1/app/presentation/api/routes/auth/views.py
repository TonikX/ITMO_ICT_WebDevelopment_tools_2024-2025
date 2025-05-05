from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from app.domain.entities.users import User
from app.presentation.api.dependencies import get_user
from app.presentation.api.routes.auth.schemas import LoginSchema, GetJWTTokenSchema, RegisterSchema, RefreshTokenSchema, \
    UpdatePasswordSchema
from app.services.auth import AuthenticationService
from app.services.exceptions import PasswordIsIncorrect, TokenExpired, InvalidToken, UsernameAlreadyExists, \
    EntityNotFound

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
    route_class=DishkaRoute
)


@router.post(
    "/login",
    response_model=GetJWTTokenSchema,
)
async def login(
        body: LoginSchema,
        auth_service: FromDishka[AuthenticationService]
):
    try:
        jwt = await auth_service.login(
            username=body.username,
            password=body.password
        )
    except PasswordIsIncorrect:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )
    except EntityNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    return GetJWTTokenSchema(
        token=jwt.token,
        expires_at=jwt.expires_at
    )


@router.post(
    "/register",
    response_model=GetJWTTokenSchema,
)
async def register(
        body: RegisterSchema,
        auth_service: FromDishka[AuthenticationService]
):
    try:
        jwt = await auth_service.register(
            username=body.username,
            password=body.password
        )
    except UsernameAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    return GetJWTTokenSchema(
        token=jwt.token,
        expires_at=jwt.expires_at
    )


@router.post(
    "/refresh-token",
    response_model=GetJWTTokenSchema,
)
async def refresh_token(
        body: RefreshTokenSchema,
        auth_service: FromDishka[AuthenticationService]
):
    try:
        jwt = await auth_service.refresh_token(body.token)
    except TokenExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен устарел"
        )
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )
    return GetJWTTokenSchema(
        token=jwt.token,
        expires_at=jwt.expires_at
    )


@router.post(
    "/change-password",
)
async def change_password(
        body: UpdatePasswordSchema,
        auth_service: FromDishka[AuthenticationService],
        user: User = Depends(get_user)
):
    try:
        await auth_service.change_password(
            user_id=user.id,
            old_password=body.old_password,
            new_password=body.new_password
        )
    except PasswordIsIncorrect:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )
