from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ...models import User
from ..users.user_security import get_current_admin_user, get_session
from ...celery_app import celery_app
from celery.result import AsyncResult

router = APIRouter(prefix="/queue", tags=["queue"])


class QueueParseRequest(BaseModel):
    urls: List[HttpUrl]
    parser_type: str = "async"


class QueueTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None


@router.post("/parse", response_model=QueueTaskResponse)
async def queue_parsing_task(
        request: QueueParseRequest,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_admin_user)
):
    """
    Ставит задачу парсинга в очередь Celery
    Доступно только администраторам
    """
    try:
        # Преобразуем URLs в строки
        urls_str = [str(url) for url in request.urls]

        # Запускаем задачу в Celery
        task = celery_app.send_task(
            'parse_sports_data',
            args=[urls_str, request.parser_type]
        )

        return QueueTaskResponse(
            task_id=task.id,
            status="queued",
            message=f"Parsing task queued with {request.parser_type} parser"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue task: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=QueueTaskResponse)
async def get_queue_task_status(
        task_id: str,
        current_user: User = Depends(get_current_admin_user)
):
    """
    Получает статус задачи из очереди Celery
    """
    try:
        result = AsyncResult(task_id, app=celery_app)

        if result.state == 'PENDING':
            return QueueTaskResponse(
                task_id=task_id,
                status="pending",
                message="Task is waiting in queue"
            )
        elif result.state == 'PROGRESS':
            return QueueTaskResponse(
                task_id=task_id,
                status="progress",
                message="Task is in progress",
                result=result.info
            )
        elif result.state == 'SUCCESS':
            return QueueTaskResponse(
                task_id=task_id,
                status="success",
                message="Task completed successfully",
                result=result.result
            )
        elif result.state == 'FAILURE':
            return QueueTaskResponse(
                task_id=task_id,
                status="failure",
                message=f"Task failed: {str(result.info)}",
                result={"error": str(result.info)}
            )
        else:
            return QueueTaskResponse(
                task_id=task_id,
                status=result.state.lower(),
                message=f"Task state: {result.state}",
                result=result.info if result.info else None
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.delete("/task/{task_id}")
async def cancel_queue_task(
        task_id: str,
        current_user: User = Depends(get_current_admin_user)
):
    """
    Отменяет задачу в очереди
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} has been cancelled"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )


@router.get("/active")
async def get_active_tasks(
        current_user: User = Depends(get_current_admin_user)
):
    """
    Получает список активных задач
    """
    try:
        inspect = celery_app.control.inspect()

        # Получаем активные задачи
        active_tasks = inspect.active()

        # Получаем задачи в ожидании
        reserved_tasks = inspect.reserved()

        return {
            "active_tasks": active_tasks,
            "reserved_tasks": reserved_tasks
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active tasks: {str(e)}"
        )


@router.get("/stats")
async def get_queue_stats(
        current_user: User = Depends(get_current_admin_user)
):
    """
    Получает статистику очереди
    """
    try:
        inspect = celery_app.control.inspect()

        stats = inspect.stats()
        registered_tasks = inspect.registered()

        return {
            "stats": stats,
            "registered_tasks": registered_tasks
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue stats: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_completed_tasks(
        current_user: User = Depends(get_current_admin_user)
):
    """
    Запускает очистку завершенных задач
    """
    try:
        task = celery_app.send_task('cleanup_old_tasks')

        return {
            "message": "Cleanup task started",
            "cleanup_task_id": task.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start cleanup: {str(e)}"
        )