from typing import Annotated

from fastapi import Depends
from core.depends import get_session
from profiles.services import ProfileService
from sqlalchemy.ext.asyncio import AsyncSession


def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileService:
    return ProfileService(session)
