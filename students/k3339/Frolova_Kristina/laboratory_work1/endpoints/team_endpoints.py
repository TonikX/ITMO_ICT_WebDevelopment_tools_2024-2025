from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from model.models.models import Team
from model.schemas.team import TeamCreate
from db.connection import get_session

team_router = APIRouter()


@team_router.get("/", response_model=list[Team])
def get_teams(session: Session = Depends(get_session)):
    return session.exec(select(Team)).all()


@team_router.get("/{team_id}", response_model=Team)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@team_router.post("/", response_model=Team, status_code=201)
def create_team(team: TeamCreate, session: Session = Depends(get_session)):
    db_team = Team.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_router.patch("/{team_id}", response_model=Team)
def update_team(team_id: int, team_data: TeamCreate, session: Session = Depends(get_session)):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    update_data = team_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_team, key, value)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_router.delete("/{team_id}", status_code=204)
def delete_team(team_id: int, session: Session = Depends(get_session)):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(db_team)
    session.commit()
    return {"message": "Team deleted"}
