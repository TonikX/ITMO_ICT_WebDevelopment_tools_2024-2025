from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession


from teams.dtos import (
    MemberAddDTO,
    MemberDTO,
    TaskCreateDTO,
    TaskDTO,
    TaskUpdateDTO,
    TeamCreateDTO,
    TeamDTO,
)
from teams.models import Member, Role, Task, Team
from users.dtos import UserDTO
from users.models import User


class TeamService:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def check_user_has_role(
        self,
        me: UserDTO,
        team_id: int,
        role: Optional[Role] = None,
    ) -> bool:
        stmt = exists().where(Team.id == team_id).select()
        is_team_exists = (await self._session.execute(stmt)).scalar()
        if not is_team_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        stmt = select(Member).where(Member.team_id == team_id, Member.user_id == me.id)
        member = (await self._session.execute(stmt)).scalar()
        if member is None:
            return False

        # role is None => any role
        if role is None:
            return True

        return member.role == role

    async def create_team(self, me: UserDTO, dto: TeamCreateDTO) -> TeamDTO:
        team = Team(**dto.model_dump())
        self._session.add(team)
        await self._session.flush()

        member = Member(
            user_id=me.id,
            team_id=team.id,
            role=Role.OWNER,
        )

        self._session.add(member)
        await self._session.commit()
        await self._session.refresh(team)

        return TeamDTO.model_validate(team)

    async def get_team_members(self, team_id: int) -> list[MemberDTO]:
        stmt = (
            select(Member)
            .where(Member.team_id == team_id)
            .options(joinedload(Member.user, innerjoin=True))
        )

        members = (await self._session.execute(stmt)).scalars().all()
        return [MemberDTO.model_validate(member) for member in members]

    async def get_member_tasks(self, member_id: int) -> list[TaskDTO]:
        stmt = exists().where(Member.id == member_id).select()
        is_member_exist = (await self._session.execute(stmt)).scalar()
        if not is_member_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        stmt = select(Task).where(Task.member_id == member_id)
        tasks = (await self._session.execute(stmt)).scalars().all()
        return [TaskDTO.model_validate(task) for task in tasks]

    async def add_team_member(self, team_id: int, dto: MemberAddDTO) -> None:
        user = await self._session.get(User, dto.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        team = await self._session.get(Team, team_id)
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found",
            )

        stmt = (
            exists()
            .where(Member.user_id == dto.user_id, Member.team_id == team_id)
            .select()
        )

        is_member_exist = (await self._session.execute(stmt)).scalar()
        if is_member_exist:
            return

        member = Member(**dto.model_dump(), team_id=team.id)
        self._session.add(member)
        await self._session.commit()

    async def remove_team_member(self, member_id: int) -> None:
        member = await self._session.get(Member, member_id)
        if member is not None:
            await self._session.delete(member)

    async def create_task(self, dto: TaskCreateDTO) -> TaskDTO:
        stmt = exists().where(Member.id == dto.member_id).select()
        is_member_exist = (await self._session.execute(stmt)).scalar()
        if not is_member_exist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        task = Task(**dto.model_dump())
        self._session.add(task)
        await self._session.commit()
        await self._session.refresh(task)

        return TaskDTO.model_validate(task)

    async def update_task(self, task_id: int, dto: TaskUpdateDTO) -> TaskDTO:
        stmt = select(Task).where(Task.id == task_id)
        task = (await self._session.execute(stmt)).scalar()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found",
            )

        dict_dto = dto.model_dump(exclude_unset=True)
        for key, value in dict_dto.items():
            setattr(task, key, value)

        self._session.add(task)
        await self._session.commit()
        await self._session.refresh(task)

        return TaskDTO.model_validate(task)
