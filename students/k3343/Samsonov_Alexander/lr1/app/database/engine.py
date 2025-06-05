from sqlalchemy.ext.asyncio import create_async_engine

from app.settings import settings

engine = create_async_engine(settings.postgres_dsn, echo=True, future=True)
