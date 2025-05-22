import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.event import Event
from app.repositories.base import BaseRepository
from app.schemas.event import EventInDb, EventBase


class EventRepository(BaseRepository[Event, EventBase, EventInDb]):
    async def filter_events_by_dates(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            from_date: Optional[datetime.date] = None,
            to_date: Optional[datetime.date] = None,
            due_register_date: Optional[datetime.date] = None
    ) -> List[Event]:
        query = select(self.model)

        if from_date:
            query = query.filter(self.model.dt_event_start >= from_date)
        if to_date:
            query = query.filter(self.model.dt_event_end <= to_date)
        if due_register_date:
            query = query.filter(self.model.dt_end_registration >= due_register_date)

        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()


event_repository = EventRepository(Event)
