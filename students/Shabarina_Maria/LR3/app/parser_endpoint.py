from fastapi import APIRouter
from app.async_parser import run_parser
from app.tasks import run_parser_task
import asyncio


parser_router = APIRouter()


def sync_parser_runner():
    asyncio.run(run_parser())


@parser_router.post("/parse/matchtv", tags=['Parser'], status_code=202)
def trigger_parser():
    run_parser_task.delay()
    return {"message": "Парсинг запущен в фоне через Celery"}
