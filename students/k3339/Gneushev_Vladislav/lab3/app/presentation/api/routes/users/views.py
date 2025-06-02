from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from app.domain.entities.users import User
from app.presentation.api.decorators.only_admin import only_admin
from app.presentation.api.dependencies import get_user
from app.presentation.api.routes.users.schemas import GetUserSchema
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
    route_class=DishkaRoute
)


@router.get(
    "/me",
    response_model=GetUserSchema,
)
async def get_me(
        user: User = Depends(get_user)
):
    return GetUserSchema(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin
    )


@router.get(
    "",
    response_model=list[GetUserSchema],
)
@only_admin
async def get_users(
        user_service: FromDishka[UserService],
):
    users = await user_service.get_users()
    return [
        GetUserSchema(
            id=user.id,
            username=user.username,
            is_admin=user.is_admin
        )
        for user in users
    ]
