from sqlalchemy import select

from app.domain.entities.users import User
from app.infrastructure.database.converters.universal import from_entity_to_db, from_db_to_entity
from app.infrastructure.database.converters.users import from_user_dm_to_db
from app.infrastructure.database.models.users import UserDB
from app.infrastructure.database.repositories.base import BaseRepository
from app.services.exceptions import EntityNotFound


class UserRepository(BaseRepository):
    async def add_user(self, user: User) -> User:
        user_db = from_user_dm_to_db(user)
        self.session.add(user_db)
        await self.session.commit()
        await self.session.refresh(user_db)
        return from_db_to_entity(user_db, User)

    async def get_user_by_username(self, username: str) -> User | None:
        q = select(UserDB).where(UserDB.username == username)
        result = await self.session.execute(q)
        user = result.scalars().first()
        if user:
            return from_db_to_entity(user, User)

    async def get_user_by_id(self, user_id: int) -> User | None:
        q = select(UserDB).where(UserDB.id == user_id)
        result = await self.session.execute(q)
        user = result.scalars().first()
        if user:
            return from_db_to_entity(user, User)

    async def update_user(self, user: User) -> User:
        user_db = await self.session.get(UserDB, user.id)

        # Обновляем поля
        user_db.username = user.username
        user_db.password_hash = user.password_hash
        user_db.is_admin = user.is_admin
        await self.session.commit()

        return await self.get_user_by_id(user.id)

    async def get_users(self) -> list[User]:
        q = select(UserDB)
        result = await self.session.execute(q)
        users = result.scalars().all()
        return [from_db_to_entity(user, User) for user in users]
