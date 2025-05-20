from fastapi import FastAPI, BackgroundTasks
from .db import parse_and_save
from .parser import urls
from .tasks import parse_books_task
from celery_worker.celery_worker import celery as celery_app
from celery.result import AsyncResult


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Parser app is running"}


@app.post("/parse")
def run_parser(background_tasks: BackgroundTasks):
    for genre, url in urls.items():
        background_tasks.add_task(parse_and_save, url, genre, 3)
    return {"message": "Parsing is running"}


@app.post("/celery-trigger")
def trigger_parse():
    task = celery_app.send_task('parser_app.tasks.parse_books_task')
    return {"task_id": task.id}


@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result
    }
