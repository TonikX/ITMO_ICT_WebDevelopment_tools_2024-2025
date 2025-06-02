from celery import Celery
import os

# Настройки Celery
REDIS_HOST = os.getenv("REDIS_HOST", "redis") # Имя сервиса Redis в Docker Compose
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0") # Номер базы данных Redis

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


# Создаем экземпляр Celery приложения
app = Celery(
    'parser_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['common.tasks']
)

app.conf.update(
    enable_utc=True,
    timezone='Europe/Moscow',
    result_expires=3600, # Результаты задач будут храниться 1 час
    task_track_started=True # Позволяет отслеживать задачи в статусе "STARTED"
)