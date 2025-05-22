from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import user_repository
from app.core.auth import verify_password
from app.schemas.user import UserInDB, UserCreate


class UserService:
    async def authenticate(
        self, db: AsyncSession, username: str, password: str
    ) -> UserInDB | None:
        user = await user_repository.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_by_username(self, db: AsyncSession, username: str) -> UserInDB | None:
        return await user_repository.get_by_username(db, username)

    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> UserInDB:
        return await user_repository.create(db, user_data)

    async def change_password(
        self, db: AsyncSession, user: UserInDB, current_password: str, new_password: str
    ) -> UserInDB:
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        return await user_repository.update_password(db, user, new_password)

user_service = UserService()