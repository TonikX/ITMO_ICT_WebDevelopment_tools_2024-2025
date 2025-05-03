from typing import Annotated
from fastapi import APIRouter, Depends

from teams.depends import check_user_is_member, check_user_is_owner, get_team_service
from teams.dtos import MemberAddDTO, TaskCreateDTO, TaskUpdateDTO, TeamCreateDTO
from teams.services import TeamService
from users.depends import get_current_user
from users.dtos import UserDTO

router = APIRouter(prefix="/teams")


@router.post("/")
async def create_team(
    curent_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[TeamService, Depends(get_team_service)],
    dto: TeamCreateDTO,
):
    return await service.create_team(me=curent_user, dto=dto)


@router.get("/{team_id}/members", dependencies=[Depends(check_user_is_member)])
async def get_team_members(
    team_id: int,
    service: Annotated[TeamService, Depends(get_team_service)],
):
    members = await service.get_team_members(team_id)
    return {"members": members}


@router.post("/{team_id}/members", dependencies=[Depends(check_user_is_owner)])
async def add_team_member(
    team_id: int,
    service: Annotated[TeamService, Depends(get_team_service)],
    dto: MemberAddDTO,
):
    await service.add_team_member(team_id=team_id, dto=dto)


@router.delete(
    "/{team_id}/members/{member_id}",
    dependencies=[Depends(check_user_is_owner)],
)
async def remove_team_member(
    member_id: int,
    service: Annotated[TeamService, Depends(get_team_service)],
):
    await service.remove_team_member(member_id)


@router.get(
    "/{team_id}/members/{member_id}/tasks",
    dependencies=[Depends(check_user_is_member)],
)
async def get_member_tasks(
    member_id: int,
    service: Annotated[TeamService, Depends(get_team_service)],
):
    tasks = await service.get_member_tasks(member_id)
    return {"tasks": tasks}


@router.post("/{team_id}/tasks", dependencies=[Depends(check_user_is_member)])
async def create_task(
    service: Annotated[TeamService, Depends(get_team_service)],
    dto: TaskCreateDTO,
):
    return await service.create_task(dto)


@router.patch(
    "/{team_id}/tasks/{task_id}",
    dependencies=[Depends(check_user_is_member)],
)
async def update_task(
    task_id: int,
    service: Annotated[TeamService, Depends(get_team_service)],
    dto: TaskUpdateDTO,
):
    return await service.update_task(task_id=task_id, dto=dto)
