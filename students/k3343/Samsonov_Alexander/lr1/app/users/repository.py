from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.users.model import User


class UserRepository:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self._session.get(User, user_id)
