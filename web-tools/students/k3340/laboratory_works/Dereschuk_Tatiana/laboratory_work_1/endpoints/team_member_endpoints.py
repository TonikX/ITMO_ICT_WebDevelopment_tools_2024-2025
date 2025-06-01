from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import List

from db.connection import get_session
from model.models.models import TeamMember
from model.schemas.team_member import TeamMemberRead, TeamMemberCreate, TeamMemberUpdate

team_member_router = APIRouter()

@team_member_router.post("/", response_model=TeamMemberRead)
def create_team_member(member: TeamMemberCreate, session: Session = Depends(get_session)):
    db_member = TeamMember.model_validate(member)
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member


@team_member_router.get("/", response_model=List[TeamMemberRead])
def get_team_members(session: Session = Depends(get_session)):
    return session.exec(select(TeamMember)).all()


@team_member_router.get("/{team_id}/user/{user_id}", response_model=TeamMemberRead)
def get_team_member(team_id: int, user_id: int, session: Session = Depends(get_session)):
    member = session.get(TeamMember, (team_id, user_id))
    if not member:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    return member


@team_member_router.patch("/{team_id}/user/{user_id}", response_model=TeamMemberRead)
def update_team_member(team_id: int, user_id: int, update: TeamMemberUpdate, session: Session = Depends(get_session)):
    member = session.get(TeamMember, (team_id, user_id))
    if not member:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    session.commit()
    session.refresh(member)
    return member


@team_member_router.delete("/{team_id}/user/{user_id}", response_model=dict)
def delete_team_member(team_id: int, user_id: int, session: Session = Depends(get_session)):
    member = session.get(TeamMember, (team_id, user_id))
    if not member:
        raise HTTPException(status_code=404, detail="TeamMember not found")
    session.delete(member)
    session.commit()
    return {"ok": True}