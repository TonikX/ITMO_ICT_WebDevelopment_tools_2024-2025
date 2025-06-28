from celery import Celery
from celery.schedules import crontab

app = Celery('myapp', broker='redis://localhost:6379/0')

# Настройка расписания
app.conf.beat_schedule = {
    # Задача, которая выполняется каждые 10 минут
    'add-every-10-minutes': {
        'task': 'tasks.add',
        'schedule': 600.0,  # в секундах
        'args': (16, 16),
    },
    # Задача, которая выполняется каждый день в 7:30 утра
    'add-every-monday-morning': {
        'task': 'tasks.add',
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'args': (16, 16),
    },
}

@app.task
def add(x, y):
    return x + y