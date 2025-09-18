from fastapi import Depends, APIRouter
from sqlmodel import Session
from typing import List

from app.auth import auth_handler
from app.controolers import teams_controller
from app.models import Team, TeamFull, TeamCreate, TeamUpdate
from database import get_session

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/get-all", response_model=List[Team])
def teams_list(session: Session = Depends(get_session)):
    return teams_controller.get_all_teams(session)


@router.get("/get-one/{team_id}", response_model=TeamFull)
def team_get_one(team_id: int, session: Session = Depends(get_session)):
    return teams_controller.get_team_by_id(team_id, session)


@router.post("/create", response_model=TeamFull)
def team_create(
    team: TeamCreate,
    auth_user_id: int = Depends(auth_handler.get_user),
    session: Session = Depends(get_session),
):
    return teams_controller.create_team(team, auth_user_id, session)


@router.post("/add-member/{team_id}/{user_id}", response_model=TeamFull)
def add_team_member(
    team_id: int,
    user_id: int,
    user_role: str | None = None,
    auth_user_id: int = Depends(auth_handler.get_user),
    session: Session = Depends(get_session),
):
    return teams_controller.add_member(team_id, user_id, user_role, auth_user_id, session)


@router.delete("/delete-member/{team_id}/{user_id}", response_model=TeamFull)
def delete_team_member(
    team_id: int,
    user_id: int,
    auth_user_id: int = Depends(auth_handler.get_user),
    session: Session = Depends(get_session),
):
    return teams_controller.delete_member(team_id, user_id, auth_user_id, session)


@router.patch("/update/{team_id}", response_model=TeamFull)
def team_update(
    team_id: int,
    updates: TeamUpdate,
    auth_user_id: int = Depends(auth_handler.get_user),
    session: Session = Depends(get_session),
):
    return teams_controller.update_team(team_id, updates, auth_user_id, session)


@router.delete("/delete-team/{team_id}")
def team_delete(
    team_id: int,
    auth_user_id: int = Depends(auth_handler.get_user),
    session: Session = Depends(get_session),
):
    return teams_controller.delete_team(team_id, auth_user_id, session)
