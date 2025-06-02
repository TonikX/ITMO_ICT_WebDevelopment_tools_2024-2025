from datetime import datetime, timezone

from app.domain.entities.jwt import JWTToken
from app.domain.entities.users import User
from app.domain.hashing import get_string_hash
from app.infrastructure.database.repositories.users import UserRepository
from app.services.exceptions import EntityNotFound, PasswordIsIncorrect, TokenExpired, UsernameAlreadyExists
from app.services.jwt import JWTService


class AuthenticationService:
    def __init__(self, user_repository: UserRepository, jwt_service: JWTService):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    async def register(self, username: str, password: str) -> JWTToken:
        user = await self.user_repository.get_user_by_username(username)
        if user:
            raise UsernameAlreadyExists()

        password_hash = get_string_hash(password)
        user = await self.user_repository.add_user(
            User(
                id=None,
                username=username,
                password_hash=password_hash,
                is_admin=False
            )
        )
        jwt = self.jwt_service.create_token(user.id)
        return jwt

    async def login(self, username: str, password: str) -> JWTToken:
        user = await self.user_repository.get_user_by_username(username)
        if not user:
            raise EntityNotFound(
                entity=User,
                field_name="username",
                value=username
            )
        password_hash = get_string_hash(password)
        if user.password_hash != password_hash:
            raise PasswordIsIncorrect()

        jwt = self.jwt_service.create_token(user.id)
        return jwt

    async def refresh_token(self, token: str) -> JWTToken:
        payload = self.jwt_service.decode_token(token)
        if payload.expires_at < datetime.now(timezone.utc):
            raise TokenExpired()
        jwt = self.jwt_service.create_token(payload.user_id)
        return jwt

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise EntityNotFound(
                entity=User,
                field_name="id",
                value=user_id
            )

        # Проверяем что старый пароль совпадает
        old_password_hash = get_string_hash(old_password)
        if user.password_hash != old_password_hash:
            raise PasswordIsIncorrect()

        # Обновляем пароль
        new_password_hash = get_string_hash(new_password)
        await self.user_repository.update_user(
            User(
                id=user.id,
                username=user.username,
                password_hash=new_password_hash,
                is_admin=user.is_admin
            )
        )
