from fastapi import Response, APIRouter
from sqlalchemy import select, exc, insert, delete, update
from sqlalchemy.orm import contains_eager, aliased, joinedload

from db.database import DatabaseSession
from db.models import Task as TaskModel, TaskLink as TaskLinkModel, Sprint as SprintModel
from rest.task.schemas import (
    TaskResponse,
    TaskBodySchema,
    MessageResponse,
    NotFoundDataResponse,
    TaskDataResponse,
    TaskWithLinksResponse,
    TaskWithLinksDataResponse,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
def get_tasks(session: DatabaseSession) -> list[TaskWithLinksResponse]:
    stmt = (
        select(TaskModel)
        .options(joinedload(TaskModel.sprint))
        .order_by(TaskModel.id)
    )
    task_models = session.scalars(stmt).unique().all()
    return [TaskWithLinksResponse.model_validate(task_model) for task_model in task_models]


@router.get("/{task_id}", responses={200: {"model": TaskWithLinksDataResponse}, 404: {"model": NotFoundDataResponse}})
def get_task(task_id: int, session: DatabaseSession, response: Response):
    # First, get the task with its sprint
    stmt = (
        select(TaskModel)
        .options(joinedload(TaskModel.sprint))
        .where(TaskModel.id == task_id)
    )
    try:
        task_model = session.scalars(stmt).unique().one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Task not found")

    return TaskWithLinksDataResponse(status=200, data=TaskWithLinksResponse.model_validate(task_model))


@router.post("/", responses={200: {"model": TaskDataResponse}, 404: {"model": NotFoundDataResponse}})
def add_task(task_body: TaskBodySchema, session: DatabaseSession, response: Response):
    insert_cte = (
        insert(TaskModel)
        .values(
            summary=task_body.summary,
            priority=task_body.priority,
            description=task_body.description,
            planned_end_at=task_body.planned_end_at,
            status=task_body.status,
            sprint_id=task_body.sprint_id,
        )
        .returning(TaskModel)
        .cte("task")
    )
    stmt = (
        select(TaskModel)
        .from_statement(
            select(insert_cte.columns, SprintModel).join(
                SprintModel, onclause=insert_cte.c.sprint_id == SprintModel.id, isouter=True
            )
        )
        .options(contains_eager(TaskModel.sprint))
    )
    try:
        task_model = session.scalars(stmt).one()
        # Commit the transaction to ensure the task is saved to the database
        session.commit()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Task not found")

    return TaskDataResponse(status=200, data=TaskResponse.model_validate(task_model))


@router.delete("/{task_id}", status_code=201)
def delete_task(task_id: int, session: DatabaseSession, response: Response) -> MessageResponse:
    stmt = delete(TaskModel).where(TaskModel.id == task_id)
    result = session.execute(stmt)

    if result.rowcount == 0:
        response.status_code = 404
        return MessageResponse(status=404, message="Task not found")

    session.commit()

    return MessageResponse(status=201, message="deleted")


@router.patch("/{task_id}", responses={200: {"model": TaskWithLinksDataResponse}, 404: {"model": NotFoundDataResponse}})
def update_task(task_id: int, task_body: TaskBodySchema, session: DatabaseSession, response: Response):
    # First check if the task exists
    task = session.get(TaskModel, task_id)
    if not task:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Task not found")
    
    # Update the task
    for key, value in task_body.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    
    session.commit()
    
    # Reload the task with its relationships
    session.refresh(task)
    
    return TaskWithLinksDataResponse(status=200, data=TaskWithLinksResponse.model_validate(task))
