from fastapi import Response, APIRouter
from sqlalchemy import select, exc

from db.database import DatabaseSession
from db.models import User as UserModel
from rest.user.schemas import (
    UserResponse,
    NotFoundDataResponse,
    UserDataResponse,
    UserBodySchema,
    MessageResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def get_users(session: DatabaseSession) -> list[UserResponse]:
    stmt = select(UserModel).order_by(UserModel.id)
    user_models = session.scalars(stmt).all()
    return [UserResponse.model_validate(user_model) for user_model in user_models]


@router.get("/{user_id}", responses={200: {"model": UserDataResponse}, 404: {"model": NotFoundDataResponse}})
def get_user(user_id: int, session: DatabaseSession, response: Response):
    stmt = select(UserModel).where(UserModel.id == user_id)
    try:
        user_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="User not found")

    return UserDataResponse(status=200, data=UserResponse.model_validate(user_model))


@router.post("/")
def add_user(user_body: UserBodySchema, session: DatabaseSession) -> UserDataResponse:
    user_model = UserModel(
        username=user_body.username,
        email=user_body.email,
        full_name=user_body.full_name,
        role=user_body.role,
    )
    session.add(user_model)
    session.commit()
    session.refresh(user_model)

    return UserDataResponse(status=200, data=UserResponse.model_validate(user_model))


@router.delete("/{user_id}", status_code=201)
def delete_user(user_id: int, session: DatabaseSession, response: Response) -> MessageResponse:
    stmt = select(UserModel).where(UserModel.id == user_id)
    try:
        user_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return MessageResponse(status=404, message="User not found")

    session.delete(user_model)
    session.commit()

    return MessageResponse(status=201, message="deleted")


@router.patch("/{user_id}", responses={200: {"model": UserDataResponse}, 404: {"model": NotFoundDataResponse}})
def update_user(user_id: int, user_body: UserBodySchema, session: DatabaseSession, response: Response):
    stmt = select(UserModel).where(UserModel.id == user_id)
    try:
        user_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="User not found")

    for key, value in user_body.model_dump().items():
        setattr(user_model, key, value)

    session.add(user_model)
    session.commit()
    session.refresh(user_model)

    return UserDataResponse(status=200, data=UserResponse.model_validate(user_model)) 