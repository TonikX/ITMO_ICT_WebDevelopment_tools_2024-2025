from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSession(engine.engine)
    try:
        yield session
    finally:
        await session.close()
