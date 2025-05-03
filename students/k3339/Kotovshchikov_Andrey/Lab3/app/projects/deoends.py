from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.depends import get_session
from projects.services import ProjectService


def get_project_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProjectService:
    return ProjectService(session)
