import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette import status

from connection import init_db
from auth.router import router as auth_router
from controllers.users import router as users_router
from controllers.tasks import router as tasks_router
from controllers.categories import router as categories_router
from controllers.tags import router as tags_router
from controllers.reminders import router as reminders_router

from tasks import parse_url_task

from celery.result import AsyncResult
from celery_app import celery as celery_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(categories_router)
app.include_router(tags_router)
app.include_router(reminders_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def read_root():
    return {"message": "Time Manager API"}


PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")


class ParseRequest(BaseModel):
    url: str


@app.post("/async-parse")
async def async_parse_url(request: ParseRequest):
    task = parse_url_task.delay(
        url=request.url,
        parser_service_url=os.getenv("PARSER_SERVICE_URL", "http://parser:8001")
    )
    return {
        "message": "Parsing started",
        "task_id": task.id,
        "status_url": f"/task-status/{task.id}"
    }


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.failed():
        error = task_result.result
        raise HTTPException(
            status_code=error.get('code', 500),
            detail=error.get('detail', 'Unknown error')
        )

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }