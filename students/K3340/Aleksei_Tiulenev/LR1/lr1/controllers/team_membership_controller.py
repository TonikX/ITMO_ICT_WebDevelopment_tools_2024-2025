from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from models.team_membership_model import TeamMembership, TeamMembershipCreate, TeamMembershipRead
from connection import SessionLocal
from util.auth import get_current_user

router = APIRouter()

def get_session():
    with SessionLocal() as session:
        yield session

@router.post("/", response_model=TeamMembershipRead, tags=["TeamMembership"])
def join_team(
    membership_create: TeamMembershipCreate,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):

    membership = TeamMembership(
        team_id=membership_create.team_id,
        user_id=current_user.id,
        role=membership_create.role,
        join_date=membership_create.join_date  # если не передано, можно установить текущее время
    )
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership

@router.get("/", response_model=list[TeamMembershipRead], tags=["TeamMembership"])
def list_team_memberships(session: Session = Depends(get_session)):
    memberships = session.exec(select(TeamMembership)).all()
    return memberships