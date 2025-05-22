import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.event import event_repository
from app.schemas.event import EventBase, EventInDb


class EventService:
    async def create(
            self,
            db: AsyncSession,
            event_data: EventBase,
    ) -> EventInDb | None:
        event = await event_repository.create(db, event_data)
        if event:
            return event
        return None

    async def get_events(
            self,
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            from_date: Optional[datetime.date] = None,
            to_date: Optional[datetime.date] = None,
            due_register_date: Optional[datetime.date] = None
    ) -> list[EventInDb] | None:
        if not any([from_date, to_date, due_register_date]):
            return await event_repository.get_all(db, skip=skip, limit=limit)
        return await event_repository.filter_events_by_dates(
            db,
            skip=skip,
            limit=limit,
            from_date=from_date,
            to_date=to_date,
            due_register_date=due_register_date
        )

    async def get_event_by_id(
            self,
            db: AsyncSession,
            event_id: int,
    ) -> EventInDb | None:
        return await event_repository.get(db, id=event_id)

    async def update_event(
            self,
            db: AsyncSession,
            event_data: EventBase,
            event_id: int
    ):
        obj = await self.get_event_by_id(db, event_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Event not found")
        return await event_repository.update(db, obj, event_data)


event_service = EventService()
