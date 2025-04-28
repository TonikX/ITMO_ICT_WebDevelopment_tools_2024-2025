from fastapi import Response, APIRouter
from sqlalchemy import select, exc
from sqlalchemy.orm import joinedload

from db.database import DatabaseSession
from db.models import Comment as CommentModel, Task as TaskModel, User as UserModel
from rest.comment.schemas import (
    CommentResponse,
    NotFoundDataResponse,
    CommentDataResponse,
    CommentBodySchema,
    MessageResponse,
)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/")
def get_comments(session: DatabaseSession) -> list[CommentResponse]:
    stmt = select(CommentModel).options(joinedload(CommentModel.author)).order_by(CommentModel.id)
    comment_models = session.scalars(stmt).unique().all()
    return [CommentResponse.model_validate(comment_model) for comment_model in comment_models]


@router.get("/{comment_id}", responses={200: {"model": CommentDataResponse}, 404: {"model": NotFoundDataResponse}})
def get_comment(comment_id: int, session: DatabaseSession, response: Response):
    stmt = select(CommentModel).options(joinedload(CommentModel.author)).where(CommentModel.id == comment_id)
    try:
        comment_model = session.scalars(stmt).unique().one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Comment not found")

    return CommentDataResponse(status=200, data=CommentResponse.model_validate(comment_model))


@router.post("/", responses={200: {"model": CommentDataResponse}, 404: {"model": NotFoundDataResponse}})
def add_comment(comment_body: CommentBodySchema, session: DatabaseSession, response: Response):
    # Check if task exists
    task = session.get(TaskModel, comment_body.task_id)
    if not task:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Task not found")

    # Check if user exists
    user = session.get(UserModel, comment_body.author_id)
    if not user:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="User not found")

    comment_model = CommentModel(
        content=comment_body.content,
        task_id=comment_body.task_id,
        author_id=comment_body.author_id,
    )
    session.add(comment_model)
    session.commit()
    session.refresh(comment_model)

    return CommentDataResponse(status=200, data=CommentResponse.model_validate(comment_model))


@router.delete("/{comment_id}", status_code=201)
def delete_comment(comment_id: int, session: DatabaseSession, response: Response) -> MessageResponse:
    stmt = select(CommentModel).where(CommentModel.id == comment_id)
    try:
        comment_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return MessageResponse(status=404, message="Comment not found")

    session.delete(comment_model)
    session.commit()

    return MessageResponse(status=201, message="deleted")


@router.patch("/{comment_id}", responses={200: {"model": CommentDataResponse}, 404: {"model": NotFoundDataResponse}})
def update_comment(comment_id: int, comment_body: CommentBodySchema, session: DatabaseSession, response: Response):
    stmt = select(CommentModel).options(joinedload(CommentModel.author)).where(CommentModel.id == comment_id)
    try:
        comment_model = session.scalars(stmt).unique().one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Comment not found")

    # Check if task exists
    if comment_body.task_id != comment_model.task_id:
        task = session.get(TaskModel, comment_body.task_id)
        if not task:
            response.status_code = 404
            return NotFoundDataResponse(status=404, data="Task not found")

    # Check if user exists
    if comment_body.author_id != comment_model.author_id:
        user = session.get(UserModel, comment_body.author_id)
        if not user:
            response.status_code = 404
            return NotFoundDataResponse(status=404, data="User not found")

    for key, value in comment_body.model_dump().items():
        setattr(comment_model, key, value)

    session.add(comment_model)
    session.commit()
    session.refresh(comment_model)

    return CommentDataResponse(status=200, data=CommentResponse.model_validate(comment_model)) 