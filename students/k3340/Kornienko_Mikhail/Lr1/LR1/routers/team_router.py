from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from typing import List

from connection import get_session
from util.auth import authenticate_user
from models.team_model import Team, TeamCreate, TeamWithFullDetails
from models.user_model import User

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=Team)
def create_team(team: TeamCreate, current_user: User = Depends(authenticate_user), session=Depends(get_session)):
    new_team = Team(**team.dict(), leader_id=current_user.id)
    session.add(new_team)
    session.commit()
    session.refresh(new_team)
    return new_team


@router.post("/{team_id}/join", response_model=Team)
def join_team(team_id: int, current_user: User = Depends(authenticate_user), session=Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if current_user in (team.members or []):
        raise HTTPException(status_code=400, detail="User already in the team")
    team.members.append(current_user)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.delete("/{team_id}/leave", response_model=Team)
def leave_team(team_id: int, current_user: User = Depends(authenticate_user), session=Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if current_user not in (team.members or []):
        raise HTTPException(status_code=400, detail="User is not a member of the team")
    team.members.remove(current_user)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.get("/", response_model=List[TeamWithFullDetails])
def list_teams(session=Depends(get_session)):
    return session.exec(select(Team)).all()


@router.get("/{team_id}", response_model=TeamWithFullDetails)
def get_team(team_id: int, session=Depends(get_session)) -> Team:
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
