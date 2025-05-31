# app/celery_worker.py

from celery import Celery
import requests
from sqlmodel import Session
from app.db import engine
from app.models import ParsedRecord

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)


@celery_app.task
def parse_url_task(url: str):
    """
    Асинхронная задача: запрашивает /parse у парсера и сохраняет результат в БД.
    """
    try:
        response = requests.post(
            "http://parser:8001/parse",
            json={"url": url},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

    record = ParsedRecord(
        url=url,
        content_size=data.get("content_size", 0),
        raw=data.get("content", "")
    )
    with Session(engine) as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        saved_id = record.id

    return {"saved_id": saved_id, **data}
