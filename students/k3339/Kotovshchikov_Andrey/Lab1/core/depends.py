from core.database import SQLConnection
from core.config import settings

connection = SQLConnection(database_uri=str(settings.DATABASE_URI))


async def get_session():
    session = connection.get_sesion()
    try:
        yield session
        await session.commit()
    except Exception as exc:
        await session.rollback()
        raise exc
    finally:
        await session.close()
