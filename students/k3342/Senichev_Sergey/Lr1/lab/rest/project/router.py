from fastapi import Response, APIRouter
from sqlalchemy import select, exc
from sqlalchemy.orm import joinedload

from db.database import DatabaseSession
from db.models import Project as ProjectModel
from rest.project.schemas import (
    ProjectResponse,
    NotFoundDataResponse,
    ProjectDataResponse,
    ProjectBodySchema,
    MessageResponse,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/")
def get_projects(session: DatabaseSession) -> list[ProjectResponse]:
    stmt = select(ProjectModel).options(joinedload(ProjectModel.sprints)).order_by(ProjectModel.id)
    project_models = session.scalars(stmt).unique().all()
    return [ProjectResponse.model_validate(project_model) for project_model in project_models]


@router.get("/{project_id}", responses={200: {"model": ProjectDataResponse}, 404: {"model": NotFoundDataResponse}})
def get_project(project_id: int, session: DatabaseSession, response: Response):
    stmt = select(ProjectModel).options(joinedload(ProjectModel.sprints)).where(ProjectModel.id == project_id)
    try:
        project_model = session.scalars(stmt).unique().one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Project not found")

    return ProjectDataResponse(status=200, data=ProjectResponse.model_validate(project_model))


@router.post("/")
def add_project(project_body: ProjectBodySchema, session: DatabaseSession) -> ProjectDataResponse:
    project_model = ProjectModel(
        name=project_body.name,
        description=project_body.description,
    )
    session.add(project_model)
    session.commit()
    session.refresh(project_model)

    return ProjectDataResponse(status=200, data=ProjectResponse.model_validate(project_model))


@router.delete("/{project_id}", status_code=201)
def delete_project(project_id: int, session: DatabaseSession, response: Response) -> MessageResponse:
    stmt = select(ProjectModel).where(ProjectModel.id == project_id)
    try:
        project_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return MessageResponse(status=404, message="Project not found")

    session.delete(project_model)
    session.commit()

    return MessageResponse(status=201, message="deleted")


@router.patch("/{project_id}", responses={200: {"model": ProjectDataResponse}, 404: {"model": NotFoundDataResponse}})
def update_project(project_id: int, project_body: ProjectBodySchema, session: DatabaseSession, response: Response):
    stmt = select(ProjectModel).options(joinedload(ProjectModel.sprints)).where(ProjectModel.id == project_id)
    try:
        project_model = session.scalars(stmt).unique().one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Project not found")

    for key, value in project_body.model_dump().items():
        setattr(project_model, key, value)

    session.add(project_model)
    session.commit()
    session.refresh(project_model)

    return ProjectDataResponse(status=200, data=ProjectResponse.model_validate(project_model)) 