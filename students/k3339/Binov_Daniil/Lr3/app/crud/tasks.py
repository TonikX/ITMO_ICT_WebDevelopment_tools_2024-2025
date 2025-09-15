from sqlmodel import Session, select
from typing import Optional, List
from app.models import Task, TaskCategory, Category
from app.schemas import TaskCreate, TaskRead

def create_task(session: Session, task: TaskCreate, user_id: int) -> Task:
    db_task = Task(**task.dict(exclude={"category_ids"}), user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    
    if task.category_ids:
        for cat_id in task.category_ids:
            category = session.get(Category, cat_id)
            if not category:
                raise ValueError(f"Category with id {cat_id} not found")
            assoc = TaskCategory(task_id=db_task.id, category_id=cat_id, association_priority=1)
            session.add(assoc)
        session.commit()
        session.refresh(db_task)
    
    return db_task

def get_task(session: Session, task_id: int) -> Optional[Task]:
    statement = select(Task).where(Task.id == task_id)
    return session.exec(statement).first()

def get_tasks_by_user(session: Session, user_id: int) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)
    return session.exec(statement).all()

def update_task(session: Session, task_id: int, task_update: dict) -> Optional[Task]:
    db_task = get_task(session, task_id)
    if not db_task:
        return None
    for key, value in task_update.items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def delete_task(session: Session, task_id: int) -> bool:
    db_task = get_task(session, task_id)
    if not db_task:
        return False
    session.delete(db_task)
    session.commit()
    return True