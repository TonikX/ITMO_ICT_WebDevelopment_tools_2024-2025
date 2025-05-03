from datetime import datetime, timezone
import hashlib

import jwt
from fastapi import HTTPException, status
from sqlalchemy import exists, select
from users.dtos import UserChangePasswordDTO, UserCreateDTO, UserDTO, UserTokenDTO
from users.models import JWTPayload, User
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings

type JWT = str


class UserService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def sign_up(self, dto: UserCreateDTO) -> UserTokenDTO:
        stmt = exists().where(User.email == dto.email).select()
        is_exists = (await self._session.execute(stmt)).scalar()
        if is_exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email occupied by another user",
            )

        new_user = User(
            email=dto.email,
            password=self._hash_password(dto.password),
        )

        self._session.add(new_user)
        await self._session.commit()
        await self._session.refresh(new_user)

        return UserTokenDTO(
            token=self._issue_token(new_user),
            user=UserDTO.model_validate(new_user),
        )

    async def sign_in(self, dto: UserCreateDTO) -> UserTokenDTO:
        stmt = select(User).where(User.email == dto.email)
        user = (await self._session.execute(stmt)).scalar()
        if (user is None) or (self._hash_password(dto.password) != user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return UserTokenDTO(
            token=self._issue_token(user),
            user=UserDTO.model_validate(user),
        )

    async def change_password(self, dto: UserChangePasswordDTO) -> None:
        stmt = select(User).where(User.email == dto.email)
        user = (await self._session.execute(stmt)).scalar()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if self._hash_password(dto.new_password) == user.password:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="New password must be different from old",
            )

        user.password = self._hash_password(dto.new_password)
        self._session.add(user)
        await self._session.commit()

    async def authenticate(self, token: JWT) -> UserDTO:
        payload = self._verify_token(token)
        stmt = select(User).where(User.id == int(payload.sub))
        user = (await self._session.execute(stmt)).scalar()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authenticated user",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserDTO.model_validate(user)

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _issue_token(self, user: User) -> JWT:
        timestamp = datetime.now(timezone.utc).timestamp()
        payload = JWTPayload(
            sub=str(user.id),
            iat=timestamp,
            exp=timestamp + settings.JWT_TTL,
        )

        return jwt.encode(
            payload=payload.model_dump(mode="json"),
            key=settings.JWT_SECRET,
            algorithm="HS256",
        )

    def _verify_token(self, token: JWT) -> JWTPayload:
        try:
            decoded_token = jwt.decode(
                jwt=token,
                key=settings.JWT_SECRET,
                algorithms=["HS256"],
            )

            return JWTPayload.model_validate(decoded_token)
        except (jwt.InvalidTokenError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired or invalid",
                headers={"WWW-Authenticate": "Bearer"},
            )
