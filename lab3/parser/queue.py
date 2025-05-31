from celery import Celery
from config.secrets import REDIS_DSN, DATABASE_DSN

celery = Celery("tasks", broker=REDIS_DSN, backend=REDIS_DSN)


@celery.task
def parse_in_background(pages_to_parse: int = 1):
    import asyncio

    async def parse_and_save():
        from parser.async_parser import parse
        from models.models import Account
        from auth.utils import get_password_hash
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from sqlmodel.ext.asyncio.session import AsyncSession
        import uuid

        engine = create_async_engine(DATABASE_DSN)
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        results = await parse(pages_to_parse)
        async with async_session() as session:
            for _, users in results:
                if not users:
                    continue
                for user in users:
                    name = user.get("name") or ""
                    name_parts = name.split()
                    last_name = name_parts[0] if len(name_parts) > 0 else ""
                    first_name = name_parts[1] if len(name_parts) > 1 else ""
                    account = Account(
                        username=user.get("username") or "",
                        first_name=first_name,
                        last_name=last_name,
                        email=user.get("email") or "",
                        password=get_password_hash(str(uuid.uuid4())),
                    )
                    session.add(account)
            await session.commit()
        return results

    return asyncio.run(parse_and_save())
