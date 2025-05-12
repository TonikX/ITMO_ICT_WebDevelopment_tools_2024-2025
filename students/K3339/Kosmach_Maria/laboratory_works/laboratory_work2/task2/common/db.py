from finances_lab2.task2.common.connection import get_session
from finances_lab2.task2.common.models import Task


def save_task(task_data: dict):
    with next(get_session()) as session:
        task = Task(
            title=task_data["title"],
            description=task_data["description"],
            due_date=task_data["due_date"],
            created_at=task_data["created_at"],
            owner_id=task_data["owner_id"],
            priority=task_data["priority"],
            status=task_data["status"]
        )
        session.add(task)
        session.commit()
        session.refresh(task)