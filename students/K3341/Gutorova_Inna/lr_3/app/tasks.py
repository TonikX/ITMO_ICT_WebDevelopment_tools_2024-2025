from celery_app import celery
import httpx
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DB_TIME")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery.task(bind=True, name='app.tasks.parse_url_task')
def parse_url_task(self, url: str, parser_service_url: str):
    """Синхронная версия задачи (без async/await)"""
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Parsing...'})

        # Используем синхронный клиент httpx
        with httpx.Client() as client:
            response = client.post(
                f"{parser_service_url}/parse",
                json={"url": url},
                timeout=30.0
            )
            response.raise_for_status()

            return {
                'status': 'success',
                'result': response.json()
            }

    except httpx.RequestError as e:
        return {
            'status': 'error',
            'code': 503 if isinstance(e, httpx.ConnectError) else 504,
            'detail': str(e)
        }
    except Exception as e:
        return {
            'status': 'error',
            'code': 500,
            'detail': str(e)
        }