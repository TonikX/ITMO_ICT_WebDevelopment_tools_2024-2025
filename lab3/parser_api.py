import uuid
from fastapi import Depends, FastAPI, HTTPException
from config.secrets import DATABASE_DSN
from auth.utils import get_password_hash
from models.models import Account
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from parser.async_parser import parse
from parser.queue import parse_in_background
from parser.queue import celery


async_engine = create_async_engine(
    DATABASE_DSN,
)
async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


app = FastAPI()


async def create_parsed_user(
    session: AsyncSession, username: str, first_name: str, last_name: str, email: str
):
    user = Account(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=get_password_hash(str(uuid.uuid4())),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)


@app.post("/parse")
async def parse_users(
    session: AsyncSession = Depends(get_async_session),
    pages_to_parse: int = 1,
) -> list[dict]:
    results = await parse(pages_to_parse)
    all_users = []
    for _, users in results:
        if not users:
            continue
        for user in users:
            name = user.get("name") or ""
            name_parts = name.split(maxsplit=2)
            name_parts = name.split()
            last_name = name_parts[0] if len(name_parts) > 0 else ""
            first_name = name_parts[1] if len(name_parts) > 1 else ""
            await create_parsed_user(
                session,
                username=user.get("username") or "",
                first_name=first_name,
                last_name=last_name,
                email=user.get("email") or "",
            )
            all_users.append(user)
    if not all_users:
        raise HTTPException(status_code=404, detail="No users found")
    return all_users


@app.post("/parse/async")
async def parse_users_async(
    pages_to_parse: int = 1,
):
    task = parse_in_background.delay(pages_to_parse)
    return {"task_id": task.id, "status": "started"}


@app.get("/parse/async/status/{task_id}")
def get_task_status(task_id: str):
    result = celery.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
