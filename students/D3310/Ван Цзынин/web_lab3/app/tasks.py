from app.celery_config import app
from app.dependencies import get_db
from app.models import Task
from sqlmodel import Session
from datetime import datetime

@app.task
def process_task(task_id: int):
    """模拟耗时任务：更新任务状态"""
    with Session(get_db()) as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = "completed"
            task.updated_at = datetime.now()
            db.commit()
            db.refresh(task)
            return {"task_id": task_id, "status": "success"}
        return {"task_id": task_id, "status": "not found"}