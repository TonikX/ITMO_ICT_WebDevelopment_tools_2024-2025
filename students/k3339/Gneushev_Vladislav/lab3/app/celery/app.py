from celery import Celery
import os

from dishka import make_async_container

from app.config.models import Config
from app.config.parser import load_config
from app.config.provider import ConfigProvider
from app.infrastructure.database.provider import DatabaseProvider
from app.services.provider import ServiceProvider

celery_app = Celery(
    'parser_tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
    include=[
        "app.presentation.celery"
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
) 

celery_app.conf.beat_schedule = {
    'add-every-15-secs': {
        'task': 'parse_bus_types',
        'schedule': 15.0,
        'args': ('https://www.car.info/en-se/volkswagen',)
    },
}


config = load_config(
    config_class=Config,
    env_file_path=".env"
)
container = make_async_container(
    ConfigProvider(),
    DatabaseProvider(),
    ServiceProvider(),
    context={Config: config}
)