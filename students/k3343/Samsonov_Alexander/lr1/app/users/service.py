from typing import Annotated

from fastapi.params import Depends

from app.users.model import User
from app.users.repository import UserRepository


class UserService:
    def __init__(self, repository: Annotated[UserRepository, Depends(UserRepository)]):
        self.repository = repository

    async def get_user(
        self,
        user_id: int,
    ) -> User | None:
        return await self.repository.get_by_id(user_id)
