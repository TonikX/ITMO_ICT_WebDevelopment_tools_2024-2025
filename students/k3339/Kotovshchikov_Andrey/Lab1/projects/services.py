from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from projects.dtos import ProjectCreateDTO, ProjectDTO, ProjectUpdateDTO
from projects.models import Project, Workflow
from teams.models import Member, Team
from users.dtos import UserDTO


class ProjectService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_allowed_projects(
        self, me: UserDTO, limit: int, offset: Optional[int] = None
    ) -> list[ProjectDTO]:
        stmt = (
            select(Project)
            .join(Workflow, Workflow.project_id == Project.id)
            .where(
                Workflow.team_id.in_(
                    select(Member.team_id).where(Member.user_id == me.id).subquery()
                )
            )
            .limit(limit)
            .offset(offset or 0)
        )

        projects = (await self._session.execute(stmt)).scalars().unique()
        return [ProjectDTO.model_validate(project) for project in projects]

    async def create_project(self, me: UserDTO, dto: ProjectCreateDTO) -> ProjectDTO:
        project = Project(**dto.model_dump(), owner_id=me.id)
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)

        return ProjectDTO.model_validate(project)

    async def update_project(
        self, me: UserDTO, project_id: int, dto: ProjectUpdateDTO
    ) -> ProjectDTO:
        project = await self._session.get(Project, project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        if project.owner_id != me.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )

        dict_dto = dto.model_dump(exclude_unset=True)
        for key, value in dict_dto.items():
            setattr(project, key, value)

        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)

        return ProjectDTO.model_validate(project)

    async def add_team_to_project(
        self, me: UserDTO, project_id: int, team_id: int
    ) -> None:
        project = await self._session.get(Project, project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        if project.owner_id != me.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )

        team = await self._session.get(Team, team_id)
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        if team in project.teams:
            return

        workflow = Workflow(team_id=team_id, project_id=project_id)
        self._session.add(workflow)
        await self._session.commit()
