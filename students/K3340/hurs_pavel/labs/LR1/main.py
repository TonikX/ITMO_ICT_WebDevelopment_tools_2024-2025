from fastapi import FastAPI, HTTPException, Depends
from fastapi.openapi.utils import get_openapi
from sqlmodel import Session, select
import os
import requests
from typing import List
from celery_worker import parse_url
from pydantic import BaseModel
from controllers import (
    user_controller,
    task_controller,
    time_entry_controller,
    task_assignment_controller
)

app = FastAPI(title="Time Manager API", version="1.0.0")

class URLRequest(BaseModel):
    urls: List[str]

class ParseResponse(BaseModel):
    task_id: str

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="API для приложения тайм-менеджера.",
        routes=app.routes,
    )
    # Добавляем схему безопасности в компоненты
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # Если необходимо добавить безопасную схему для всех эндпоинтов, можно сделать так:
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method].setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Переопределяем генерацию OpenAPI-схемы
app.openapi = custom_openapi

# Подключаем роутеры API
app.include_router(user_controller.router, prefix="/users", tags=["Users"])
app.include_router(task_controller.router, prefix="/tasks", tags=["Tasks"])
app.include_router(time_entry_controller.router, prefix="/time-entries", tags=["Time Entries"])
app.include_router(task_assignment_controller.router, prefix="/assignments", tags=["Task Assignments"])

@app.post("/parse/sync")
def parse_urls_sync(request: URLRequest):
    """Synchronously parse URLs using the parser service"""
    parser_url = os.getenv('PARSER_URL', 'http://localhost:8001')
    results = []
    
    for url in request.urls:
        try:
            response = requests.post(
                f"{parser_url}/parse",
                json={"url": url}
            )
            response.raise_for_status()
            results.append(response.json())
        except requests.RequestException as e:
            results.append({"error": str(e), "url": url})
    
    return results

@app.post("/parse/async", response_model=ParseResponse)
async def parse_urls_async(request: URLRequest):
    """Asynchronously parse URLs using Celery"""
    # Send task to Celery
    task = parse_url.delay(request.urls)
    return ParseResponse(task_id=task.id)

@app.get("/parse/status/{task_id}")
async def get_parse_status(task_id: str):
    """Get the status of an async parsing task"""
    task = parse_url.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "result": task.get()}
    return {"status": "processing"}