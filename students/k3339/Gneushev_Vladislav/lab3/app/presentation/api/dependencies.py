from datetime import datetime, timezone

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import HTTPException, Header, Depends
from starlette import status

from app.domain.entities.jwt import JWTTokenPayload
from app.services.exceptions import InvalidToken, EntityNotFound, TokenExpired
from app.services.jwt import JWTService
from app.services.users import UserService


@inject
async def get_token_payload(
        jwt_service: FromDishka[JWTService],
        token: str = Header(alias='Authorization')
) -> JWTTokenPayload:
    token = token.split(' ')[-1]
    try:
        payload = jwt_service.decode_token(token)
    except InvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный токен'
        )
    except TokenExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен устарел'
        )
    if payload.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен устарел'
        )
    return payload


@inject
async def get_user(
        user_service: FromDishka[UserService],
        jwt_token: JWTTokenPayload = Depends(get_token_payload)
):
    try:
        user = await user_service.get_user(jwt_token.user_id)
    except EntityNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Ошибка аутентификации (пользователь не найден)'
        )
    return user
