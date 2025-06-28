from typing import List


from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.project import Project
from app.models.team_member import TeamMember
from app.schemas.project import ProjectCreate, ProjectOut
from app.models.profile import Profile

router = APIRouter(prefix="/projects", tags=["Projects"])

# Создать проект
@router.post("/", response_model=ProjectOut)
def create_project(project_data: ProjectCreate, session: Session = Depends(get_session)):
    db_project = Project(**project_data.dict())
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

# Получить все проекты
@router.get("/", response_model=List[ProjectOut])
def read_projects(session: Session = Depends(get_session)):
    projects = session.query(Project).all()
    return projects

# Получить проект по ID
@router.get("/{project_id}", response_model=ProjectOut)
def read_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project