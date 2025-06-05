from celery import Celery
import os
import httpx
import asyncio
from typing import List

celery_app = Celery(
    "hockey_parser",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379"),
    include=['app.celery_tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_result_expires=3600,  # 1 час
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@celery_app.task(bind=True, name='parse_sports_data')
def parse_sports_data_task(self, urls: List[str], parser_type: str = "async"):
    """
    Celery задача для парсинга спортивных данных
    """
    try:
        # Обновляем статус задачи
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Starting parser service request...'}
        )

        import requests

        parser_url = "http://parser:8001"

        response = requests.post(
            f"{parser_url}/parse",
            json={
                "urls": urls,
                "parser_type": parser_type
            },
            timeout=30
        )
        response.raise_for_status()
        parser_task = response.json()

        parser_task_id = parser_task["task_id"]

        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Parser started, waiting for completion...',
                'parser_task_id': parser_task_id
            }
        )

        import time
        max_wait_time = 300  # 5 минут максимум
        wait_time = 0
        check_interval = 5  # проверяем каждые 5 секунд

        while wait_time < max_wait_time:
            time.sleep(check_interval)
            wait_time += check_interval

            # Проверяем статус
            status_response = requests.get(
                f"{parser_url}/status/{parser_task_id}",
                timeout=10
            )

            if status_response.status_code == 200:
                status_data = status_response.json()

                if status_data["status"] == "completed":
                    return {
                        'status': 'completed',
                        'message': 'Parsing completed successfully',
                        'teams_parsed': status_data.get('teams_parsed', 0),
                        'schools_created': status_data.get('schools_created', 0),
                        'tournaments_created': status_data.get('tournaments_created', 0),
                        'parser_task_id': parser_task_id
                    }
                elif status_data["status"] == "failed":
                    return {
                        'status': 'failed',
                        'message': f'Parsing failed: {status_data.get("message", "Unknown error")}',
                        'parser_task_id': parser_task_id
                    }
                else:
                    # Обновляем прогресс
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'status': f'Parser status: {status_data["status"]}',
                            'message': status_data.get('message', ''),
                            'parser_task_id': parser_task_id
                        }
                    )

        # Таймаут
        return {
            'status': 'timeout',
            'message': 'Parsing task timed out',
            'parser_task_id': parser_task_id
        }

    except requests.RequestException as e:
        return {
            'status': 'failed',
            'message': f'Parser service error: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'failed',
            'message': f'Task execution error: {str(e)}'
        }


@celery_app.task(bind=True, name='cleanup_old_tasks')
def cleanup_old_tasks_task(self):
    """
    Задача для очистки старых задач
    """
    try:
        # Логика очистки старых задач из Redis
        # Это можно расширить для очистки завершенных задач
        return {'status': 'completed', 'message': 'Cleanup completed'}
    except Exception as e:
        return {'status': 'failed', 'message': str(e)}


if __name__ == '__main__':
    celery_app.start()