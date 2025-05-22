from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.auth import get_password_hash
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_active=True
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_password(self, db: AsyncSession, user: User, new_password: str) -> User | None:
        db_obj = (await db.execute(select(User).filter(User.id == user.id))).scalars().first()
        db_obj.hashed_password = get_password_hash(new_password)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


user_repository = UserRepository(User)
