from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Team, User, Event
from app.repositories.team import team_repository
from app.schemas.team import TeamCreate


class TeamService:
    async def get_event_teams(self, db: AsyncSession, event_id) -> List[Team]:
        result = await team_repository.get_event_teams(db, event_id)
        return result

    async def get_user_teams(self, db: AsyncSession, current_user: User) -> List[Team]:
        result = await team_repository.get_user_teams(db, current_user.id)
        return result

    async def create_team(self, db, team_data: TeamCreate, event: Event) -> Team:
        data = team_data.model_dump()
        data['event_id'] = event.id
        data['event'] = event
        result = await team_repository.create(db, Team(**data))
        return result


team_service = TeamService()