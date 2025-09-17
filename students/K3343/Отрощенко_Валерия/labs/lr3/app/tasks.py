import os
import asyncio
from .celery_app import app
from .main_parser import parse_urls   # <--- исправили импорт
from .config import NUM_WORKERS

# единый дефолтный DSN, совпадающий с твоей БД
DEFAULT_DSN = os.getenv("DB_ADMIN", "postgresql://postgres:postgres@localhost:1928/hackathons_db")

@app.task(name="app.tasks.parse_url_task")
def parse_url_task(url: str):
    return asyncio.run(parse_urls([url], DEFAULT_DSN, NUM_WORKERS))

@app.task(name="app.tasks.parse_many_task")
def parse_many_task(urls: list[str]):
    return asyncio.run(parse_urls(urls, DEFAULT_DSN, NUM_WORKERS))