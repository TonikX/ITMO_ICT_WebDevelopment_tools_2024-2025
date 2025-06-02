from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from typing import List
import httpx
from app.config import settings
from common.tasks import parse_urls_task

router = APIRouter()

PARSER_SERVICE_URL = f"http://{settings.PARSER_HOST}:{settings.PARSER_PORT}"


class ParserRequest(BaseModel):
    urls: List[HttpUrl] = Field(..., min_length=1)
    parser_type: str = "async"

@router.post("/run-parser-async")
async def run_parser_via_celery(request: ParserRequest):
    valid_parsers = ["async", "threading", "multiprocessing"]
    if request.parser_type not in valid_parsers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parser type. Choose from {valid_parsers}"
        )

    urls_as_strings = [str(url) for url in request.urls]

    # Ставим задачу в очередь Celery
    task = parse_urls_task.delay(urls_as_strings, request.parser_type)

    return {
        "message": f"Parser task submitted to Celery for {len(urls_as_strings)} URL(s).",
        "task_id": task.id # Возвращаем ID задачи Celery для отслеживания
    }

# Эндпоинт для проверки статуса задачи Celery
@router.get("/parser-task-status/{task_id}")
async def get_parser_task_status(task_id: str):
    task = parse_urls_task.AsyncResult(task_id) # Получаем объект результата задачи по ID

    if task.state == 'PENDING': # Задача еще не началась
        response = {
            'status': task.state,
            'message': 'Task is pending or unknown.'
        }
    elif task.state == 'STARTED': # Задача началась
        response = {
            'status': task.state,
            'message': 'Task has started.'
        }
    elif task.state == 'SUCCESS': # Задача успешно завершена
        response = {
            'status': task.state,
            'result': task.result # Результат, возвращенный задачей
        }
    elif task.state == 'FAILURE': # Задача завершилась с ошибкой
        response = {
            'status': task.state,
            'message': 'Task failed.',
            'exc': str(task.info.get('exc_type')), # Тип исключения
            'exc_message': str(task.info.get('exc_message')), # Сообщение об исключении
        }
    else:
        response = {
            'status': task.state,
            'message': 'Task is in an unexpected state.',
            'info': task.info # Дополнительная информация о задаче
        }
    return response

@router.post("/run-parser")
async def run_parser(request: ParserRequest, background_tasks: BackgroundTasks):
    valid_parsers = ["async", "threading", "multiprocessing"]
    if request.parser_type not in valid_parsers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parser type. Choose from {valid_parsers}"
        )
    urls_as_strings = [str(url) for url in request.urls]
    background_tasks.add_task(trigger_parser_service, urls_as_strings, request.parser_type)
    return {"message": f"Parser {request.parser_type} started in background for {len(request.urls)} URL(s)."}

async def trigger_parser_service(urls: List[str], parser_type: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PARSER_SERVICE_URL}/parse",
                json={"urls": urls, "parser_type": parser_type}
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            print(f"Error triggering parser service: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")