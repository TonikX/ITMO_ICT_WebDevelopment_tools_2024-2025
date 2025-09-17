import asyncio
from app.celery_worker import celery_app
from app.async_parser import parse_news

@celery_app.task(name="app.tasks.parse_news_task")
def parse_news_task(count: int):
    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                fut = asyncio.ensure_future(parse_news(count))
                loop.run_until_complete(fut)
                return fut.result()
            else:
                return loop.run_until_complete(parse_news(count))
        except RuntimeError:
            return asyncio.run(parse_news(count))
    except Exception as e:
        return {"error": str(e)}