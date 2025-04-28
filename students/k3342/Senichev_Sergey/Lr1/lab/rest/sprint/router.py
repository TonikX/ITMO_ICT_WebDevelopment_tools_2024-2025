from fastapi import Response, APIRouter, Depends, HTTPException
from sqlalchemy import select, exc
from sqlalchemy.orm import Session, joinedload
from typing import List

from db.database import DatabaseSession, get_database_session
from db.models import Sprint as SprintModel, Project as ProjectModel
from rest.sprint.schemas import (
    SprintResponse,
    NotFoundDataResponse,
    SprintDataResponse,
    SprintBodySchema,
    MessageResponse,
)

router = APIRouter(prefix="/sprints", tags=["sprints"])


@router.get("/")
def get_sprints(session: DatabaseSession) -> list[SprintResponse]:
    stmt = select(SprintModel).options(joinedload(SprintModel.tasks)).order_by(SprintModel.id)
    sprint_models = session.scalars(stmt).unique().all()
    return [SprintResponse.model_validate(sprint_model) for sprint_model in sprint_models]


@router.get("/{sprint_id}", responses={200: {"model": SprintDataResponse}, 404: {"model": NotFoundDataResponse}})
def get_sprint(sprint_id: int, session: DatabaseSession, response: Response):
    stmt = select(SprintModel).options(joinedload(SprintModel.tasks)).where(SprintModel.id == sprint_id)
    try:
        sprint_model = session.scalars(stmt).unique().one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Sprint not found")

    return SprintDataResponse(status=200, data=SprintResponse.model_validate(sprint_model))


@router.post("/sprint", response_model=SprintResponse)
async def add_sprint(sprint: SprintBodySchema, db: Session = Depends(get_database_session)):
    # Check if project exists
    project = db.query(ProjectModel).filter(ProjectModel.id == sprint.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_sprint = SprintModel(
        title=sprint.title,
        start_at=sprint.start_at,
        end_at=sprint.end_at,
        project_id=sprint.project_id
    )
    db.add(new_sprint)
    db.commit()
    db.refresh(new_sprint)
    return new_sprint


@router.delete("/{sprint_id}", status_code=201)
def delete_sprint(sprint_id: int, session: DatabaseSession, response: Response) -> MessageResponse:
    stmt = select(SprintModel).where(SprintModel.id == sprint_id)
    try:
        sprint_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return MessageResponse(status=404, message="Task not found")

    session.delete(sprint_model)
    session.commit()

    return MessageResponse(status=201, message="deleted")


@router.patch("/{sprint_id}", responses={200: {"model": SprintDataResponse}, 404: {"model": NotFoundDataResponse}})
def update_sprint(sprint_id: int, sprint_body: SprintBodySchema, session: DatabaseSession, response: Response):
    stmt = select(SprintModel).where(SprintModel.id == sprint_id)
    try:
        sprint_model = session.scalars(stmt).one()
    except exc.NoResultFound:
        response.status_code = 404
        return NotFoundDataResponse(status=404, data="Task not found")

    # Check if project exists if project_id is being updated
    if sprint_body.project_id is not None:
        project = session.query(ProjectModel).filter(ProjectModel.id == sprint_body.project_id).first()
        if not project:
            response.status_code = 404
            return NotFoundDataResponse(status=404, data="Project not found")

    for key, value in sprint_body.model_dump(exclude_unset=True).items():
        setattr(sprint_model, key, value)

    session.add(sprint_model)
    session.commit()
    session.refresh(sprint_model)

    return SprintDataResponse(status=200, data=SprintResponse.model_validate(sprint_model))


@router.get("/sprints/", response_model=List[SprintResponse])
def read_sprints(skip: int = 0, limit: int = 100, db: Session = Depends(get_database_session)):
    sprints = db.query(SprintModel).offset(skip).limit(limit).all()
    return [SprintResponse.model_validate(sprint) for sprint in sprints]


@router.get("/sprints/{sprint_id}", response_model=SprintResponse)
def read_sprint(sprint_id: int, db: Session = Depends(get_database_session)):
    sprint = db.query(SprintModel).filter(SprintModel.id == sprint_id).first()
    if sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return SprintResponse.model_validate(sprint)


@router.put("/sprints/{sprint_id}", response_model=SprintResponse)
def update_sprint(sprint_id: int, sprint: SprintBodySchema, db: Session = Depends(get_database_session)):
    db_sprint = db.query(SprintModel).filter(SprintModel.id == sprint_id).first()
    if db_sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check if project exists if project_id is being updated
    if sprint.project_id is not None:
        project = db.query(ProjectModel).filter(ProjectModel.id == sprint.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in sprint.model_dump(exclude_unset=True).items():
        setattr(db_sprint, key, value)
    
    db.commit()
    db.refresh(db_sprint)
    return SprintResponse.model_validate(db_sprint)


@router.delete("/sprints/{sprint_id}")
def delete_sprint(sprint_id: int, db: Session = Depends(get_database_session)):
    db_sprint = db.query(SprintModel).filter(SprintModel.id == sprint_id).first()
    if db_sprint is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    db.delete(db_sprint)
    db.commit()
    return {"message": "Sprint deleted successfully"}


