from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models.team_model import Team, TeamCreate, TeamRead
from connection import SessionLocal
from util.auth import get_current_user

router = APIRouter()

def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/", response_model=TeamRead, tags=["Teams"])
def create_team(
    team_create: TeamCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    new_team = Team(
        team_name=team_create.team_name,
        description=team_create.description,
        creator_id=current_user.id
    )
    session.add(new_team)
    session.commit()
    session.refresh(new_team)
    return new_team

@router.get("/", response_model=list[TeamRead], tags=["Teams"])
def list_teams(session: Session = Depends(get_session)):
    teams = session.exec(select(Team)).all()
    return teams

@router.get("/{team_id}", response_model=TeamRead, tags=["Teams"])
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team