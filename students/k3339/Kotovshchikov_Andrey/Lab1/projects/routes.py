from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query

from projects.deoends import get_project_service
from projects.dtos import ProjectCreateDTO, ProjectUpdateDTO
from projects.services import ProjectService
from users.depends import get_current_user
from users.dtos import UserDTO

router = APIRouter(prefix="/projects")


@router.get("/")
async def get_allowed_projects(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
    limit: int = Query(default=100),
    offset: Optional[int] = Query(default=None),
):
    projects = await service.get_allowed_projects(
        me=current_user,
        limit=limit,
        offset=offset,
    )

    return {"projects": projects}


@router.post("/")
async def create_project(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
    dto: ProjectCreateDTO,
):
    return await service.create_project(me=current_user, dto=dto)


@router.patch("/{project_id}")
async def update_project(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
    project_id: int,
    dto: ProjectUpdateDTO,
):
    return await service.update_project(me=current_user, project_id=project_id, dto=dto)


@router.post("/{project_id}/teams/{team_id}")
async def add_team_to_project(
    project_id: int,
    team_id: int,
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    service: Annotated[ProjectService, Depends(get_project_service)],
):
    await service.add_team_to_project(
        me=current_user,
        project_id=project_id,
        team_id=team_id,
    )
