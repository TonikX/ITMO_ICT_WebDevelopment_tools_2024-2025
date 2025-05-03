from typing import Annotated
from fastapi import APIRouter, Body, Depends
from users.depends import get_current_user, get_user_service
from users.dtos import UserChangePasswordDTO, UserCreateDTO, UserDTO, UserTokenDTO
from users.services import UserService

router = APIRouter(prefix="/users")


@router.post("/sign-up", response_model=UserTokenDTO)
async def sign_up(
    dto: UserCreateDTO,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.sign_up(dto)


@router.post("/sign-in", response_model=UserTokenDTO)
async def sign_in(
    dto: UserCreateDTO,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return await service.sign_in(dto)


@router.patch("/")
async def change_password(
    service: Annotated[UserService, Depends(get_user_service)],
    dto: UserChangePasswordDTO,
):
    await service.change_password(dto)
    return {"message": "password changed successfully!"}
