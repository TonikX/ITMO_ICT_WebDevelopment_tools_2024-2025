from fastapi import FastAPI, HTTPException, Depends
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import requests

from sqlmodel import Session
from app.db import init_db, get_session
from app.utils.security import get_current_user
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.tasks import router as task_router
from app.models import ParsedRecord
from app.celery_worker import celery_app, parse_url_task

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])


@app.get("/", tags=["Home"])
def read_root():
    return {"message": "Time Manager & Parser API is running!"}


@app.get("/users/me", tags=["Users"])
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}


class URLRequest(BaseModel):
    url: str


@app.post("/parse", tags=["Parser"])
def parse_and_save(
    request: URLRequest,
    session: Session = Depends(get_session)
):
    try:
        resp = requests.post(
            "http://parser:8001/parse",
            json=request.dict(),
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    record = ParsedRecord(
        url=request.url,
        content_size=data.get("content_size", 0),
        raw=data.get("content", "")
    )
    session.add(record)
    session.commit()
    session.refresh(record)

    return {"saved_id": record.id, **data}


@app.post("/parse_async", tags=["Parser"])
def enqueue_parse_task(request: URLRequest):
    """
    Ставит парсинг в очередь Celery.
    """
    task = parse_url_task.delay(request.url)
    return {
        "task_id": task.id,
        "status": "Task has been submitted to background processing"
    }


@app.get("/parse_status/{task_id}", tags=["Parser"])
def get_parse_status(task_id: str):
    """
    Проверяет статус Celery-задачи и, если она готова, возвращает результат.
    """
    async_result = celery_app.AsyncResult(task_id)
    status = async_result.status

    result = None
    if async_result.ready():
        result = async_result.result

    return {
        "task_id": task_id,
        "status": status,
        "result": result
    }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Time Manager & Parser API",
        version="0.1.0",
        description="Комбинированный API: задачи + синхронный и асинхронный парсинг",
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path, methods in schema["paths"].items():
        for op, details in methods.items():
            if "tags" in details and "Parser" not in details["tags"]:
                details["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
