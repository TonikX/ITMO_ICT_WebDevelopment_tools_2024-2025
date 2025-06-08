from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.celery_config import celery_app
from app.dependencies import get_db
from app.models import Lab3Task
import traceback

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/submit", summary="提交任务到队列")
def submit_task(
        task_data: str,  # 任务数据（可扩展为 Pydantic 模型）
        db: Session = Depends(get_db)
):
    """
    1. 将任务初始状态写入数据库
    2. 提交到 Celery 队列异步处理
    """
    try:
        # 步骤 1：写入数据库（pending 状态）
        new_task = Lab3Task(
            status="pending",
            data=task_data,
            description="Lab3 队列任务"
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        # 步骤 2：提交到 Celery 队列（传递任务 ID）
        process_task.delay(new_task.id)

        return {
            "task_id": new_task.id,
            "status": "queued",
            "message": "任务已提交到队列，异步处理中"
        }
    except Exception as e:
        # 捕获异常，打印详细报错
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"任务提交失败：{str(e)}"
        )


@celery_app.task(name="tasks.process_task")
def process_task(task_id: int):
    """
    Celery 异步任务：模拟耗时操作 + 更新数据库状态
    1. 标记为 processing
    2. 模拟耗时逻辑（如调用外部 API）
    3. 标记为 completed
    """
    from sqlmodel import Session, create_engine
    from app.dependencies import DATABASE_URL  # 复用数据库连接
    from app.models import Lab3Task

    # 初始化数据库会话（Celery 任务中需单独创建）
    engine = create_engine(DATABASE_URL)
    with Session(engine) as db:
        task = db.get(Lab3Task, task_id)
        if not task:
            return  # 任务不存在，跳过

        # 步骤 1：标记为处理中
        task.status = "processing"
        db.commit()

        # 步骤 2：模拟耗时操作（这里用 sleep 代替实际逻辑）
        import time
        time.sleep(5)  # 模拟 5 秒处理

        # 步骤 3：标记为完成
        task.status = "completed"
        task.completed_at = datetime.now()
        db.commit()


@router.get("/{task_id}", summary="查询任务状态")
def get_task_status(
        task_id: int,
        db: Session = Depends(get_db)
):
    """查询任务的实时状态"""
    task = db.get(Lab3Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "task_id": task.id,
        "status": task.status,
        "data": task.data,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }