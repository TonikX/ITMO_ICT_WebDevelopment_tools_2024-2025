# app/api/team_members.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.profile import Profile

router = APIRouter(prefix="/team-members", tags=["Team Members"])

# Добавить участника в проект
@router.post("/")
def add_team_member(
    profile_id: int,
    project_id: int,
    role: str,
    session: Session = Depends(get_session)
):
    profile = session.get(Profile, profile_id)
    project = session.get(Project, project_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    team_member = TeamMember(profile_id=profile_id, project_id=project_id, role=role)
    session.add(team_member)
    session.commit()
    session.refresh(team_member)
    return team_member

# Получить всех участников проекта
@router.get("/project/{project_id}")
def get_project_members(project_id: int, session: Session = Depends(get_session)):
    members = session.query(TeamMember).where(TeamMember.project_id == project_id).all()
    return members

# Получить все проекты пользователя
@router.get("/profile/{profile_id}")
def get_profile_projects(profile_id: int, session: Session = Depends(get_session)):
    projects = session.query(TeamMember).where(TeamMember.profile_id == profile_id).all()
    return projects