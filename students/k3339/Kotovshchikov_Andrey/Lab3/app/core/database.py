from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
)


class SQLConnection:
    def __init__(self, database_uri: str):
        self._engine = create_async_engine(url=database_uri, echo=True)

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autocommit=False,
        )

    def get_sesion(self) -> AsyncSession:
        session = self._session_factory()
        return session

    async def close(self) -> None:
        await self._engine.dispose()
