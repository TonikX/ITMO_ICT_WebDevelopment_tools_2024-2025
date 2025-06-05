import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Story, Comment, ListHolder
from app.task_manager.hn_client import get_item_by_id

API_BASE_URL = "https://hacker-news.firebaseio.com/v0"
logging.basicConfig(
    format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO
)


@asynccontextmanager
async def get_http_client():
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=60) as client:
            yield client
    finally:
        await client.aclose()


async def insert_item(item: dict, session: AsyncSession):
    item_type = item.get("type")
    item["time"] = convert_unix_time(item["time"])
    item_id = item.get("id")

    if item_type == "story":
        obj_class = Story
    elif item_type == "comment":
        obj_class = Comment
    else:
        return None

    existing = await session.get(obj_class, item_id)

    if existing:
        for key, value in item.items():
            if key in existing.model_fields.keys():
                setattr(existing, key, value)
        await session.commit()
        await session.refresh(existing)
        return existing
    else:
        obj = obj_class(**item)
        session.add(obj)
        await session.commit()
        return obj


def convert_unix_time(unix_time: int) -> datetime:
    return datetime.fromtimestamp(unix_time)


async def recursive_get(obj_id, depth: int, session: AsyncSession):
    obj = await get_or_fetch_comment(session, obj_id)

    if depth == 0:
        return obj

    kids = obj.get("kids") or []

    kids_arr = []
    for kid in kids:
        kids_arr.append(await recursive_get(kid, depth - 1, session))

    obj["kids"] = kids_arr
    return obj


async def get_or_fetch_comment(session: AsyncSession, comment_id: int):
    existing = await session.get(Comment, comment_id)

    if existing:
        return existing.model_dump()

    async with get_http_client() as client:
        item = await get_item_by_id(comment_id, client)

    return (await insert_item(item, session)).model_dump()


async def upsert_lists(
        session: AsyncSession,
        new_ids: Optional[list[int]] = None,
        trending_ids: Optional[list[int]] = None,
        row_id: int = 1,
):
    values = {"id": row_id}
    if new_ids is not None:
        values["new_ids"] = new_ids
    if trending_ids is not None:
        values["trending_ids"] = trending_ids

    stmt = insert(ListHolder).values(**values)
    update_set = {}
    if new_ids is not None:
        update_set["new_ids"] = stmt.excluded.new_ids
    if trending_ids is not None:
        update_set["trending_ids"] = stmt.excluded.trending_ids

    if update_set:
        stmt = stmt.on_conflict_do_update(
            index_elements=[ListHolder.id],
            set_=update_set,
        )
    await session.execute(stmt)
    await session.commit()

    return await session.get(ListHolder, row_id)
