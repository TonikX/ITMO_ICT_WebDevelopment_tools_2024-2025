from app.tasks import celery_app

# Вызов из docker: celery -A app.celery_worker.celery_app worker --loglevel=info