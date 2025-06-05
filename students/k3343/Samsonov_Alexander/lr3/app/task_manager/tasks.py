import asyncio

from app.celery_worker import celery_app
from app.db.session import get_session
from app.task_manager.hn_client import get_new_stories, parse_item_array
from app.task_manager.utils import get_http_client
from app.task_manager.utils import insert_item, upsert_lists
from app.repository import ProjectRepository


@celery_app.task
def fetch_and_store_new_stories():
    async def _fetch_and_store_new_stories():
        async with get_http_client() as client:
            story_ids = await get_new_stories(client)
            items = await parse_item_array(story_ids, client)

        session = await anext(get_session())
        await upsert_lists(session, new_ids=story_ids)

        for item in items:
            await insert_item(item, session)

    asyncio.run(_fetch_and_store_new_stories())


@celery_app.task
def fetch_and_store_top_stories():
    async def _fetch_and_store_top_stories():
        async with get_http_client() as client:
            story_ids = await get_new_stories(client)
            items = await parse_item_array(story_ids, client)

        session = await anext(get_session())

        await upsert_lists(session, trending_ids=story_ids)
        for item in items:
            await insert_item(item, session)

    asyncio.run(_fetch_and_store_top_stories())


@celery_app.task
def fetch_story_comments(story_id):
    async def _fetch_story_comments(story_id):
        session = await anext(get_session())

        return await ProjectRepository().load_thread(session, story_id)

    asyncio.run(_fetch_story_comments(story_id))
