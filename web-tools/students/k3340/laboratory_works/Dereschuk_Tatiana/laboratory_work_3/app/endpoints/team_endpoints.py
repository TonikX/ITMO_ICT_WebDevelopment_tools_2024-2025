from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import List

from db.connection import get_session
from model.models.models import Team
from model.schemas.team import TeamRead, TeamCreate, TeamUpdate

team_router = APIRouter()

@team_router.post("/", response_model=TeamRead)
def create_team(team: TeamCreate, session: Session = Depends(get_session)):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_router.get("/", response_model=List[TeamRead])
def get_teams(session: Session = Depends(get_session)):
    return session.exec(select(Team)).all()


@team_router.get("/{team_id}", response_model=TeamRead)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@team_router.patch("/{team_id}", response_model=TeamRead)
def update_team(team_id: int, update: TeamUpdate, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
    session.commit()
    session.refresh(team)
    return team


@team_router.delete("/{team_id}", response_model=dict)
def delete_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}
