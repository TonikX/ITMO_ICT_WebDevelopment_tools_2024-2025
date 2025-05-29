from fastapi import Depends, HTTPException, APIRouter
from typing import Union
from typing_extensions import TypedDict
from sqlmodel import select
from auth import auth_handler
from db import get_session
from models import *

router = APIRouter()


@router.get("/get-all")
def teams_list(session=Depends(get_session)) -> List[Team]:
    return session.exec(select(Team)).all()


@router.get("/get-one/{team_id}")
def team_get_one(team_id: int, session=Depends(get_session)) -> TeamFull:
    team = session.get(Team, team_id)
    return TeamFull.model_validate(
        team,
        update={
            "members": [
                UserForTeam.model_validate(member_link.member, update={"member_role": member_link.role})
                for member_link in team.member_links
            ]
        },
    )


@router.post("/create")
def team_create(team: TeamCreate, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)) \
        -> TeamFull:
    auth_user = session.get(User, authUserId)
    if not auth_user:
        raise HTTPException(status_code=403, detail="User not found")
    team = Team.model_validate(team)
    session.add(team)
    session.commit()
    session.refresh(team)
    member_team_link = MemberTeamLink(team_id=team.id, user_id=authUserId)
    session.add(member_team_link)
    session.commit()
    session.refresh(team)
    return TeamFull.model_validate(
        team,
        update={
            "members": [
                UserForTeam.model_validate(member_link.member, update={"member_role": member_link.role})
                for member_link in team.member_links
            ]
        },
    )


@router.post("/add-member/{team_id}/{user_id}")
def add_team_member(
        team_id: int,
        user_id: int,
        user_role: str | None,
        authUserId=Depends(auth_handler.get_user),
        session=Depends(get_session)
) -> TeamFull:
    auth_member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id, MemberTeamLink.user_id == authUserId)).first()
    if auth_member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    member_team_link = MemberTeamLink(team_id=team_id, user_id=user_id, role=user_role)
    session.add(member_team_link)
    try:
        session.commit()
    except exc.IntegrityError:
        raise HTTPException(status_code=400, detail="Member already exists in this team")
    session.refresh(team)
    return TeamFull.model_validate(
        team,
        update={
            "members": [
                UserForTeam.model_validate(member_link.member, update={"member_role": member_link.role})
                for member_link in team.member_links
            ]
        },
    )


@router.delete("/delete-member/{team_id}/{user_id}")
def delete_team_member(
        team_id: int,
        user_id: int,
        authUserId=Depends(auth_handler.get_user),
        session=Depends(get_session)
) -> TeamFull:
    auth_member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id, MemberTeamLink.user_id == authUserId)).first()
    if auth_member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id, MemberTeamLink.user_id == user_id)).first()
    if member_team_link is None:
        raise HTTPException(status_code=404, detail="User not found")
    print('\n',member_team_link,'\n')
    session.delete(member_team_link)
    session.commit()
    session.refresh(team)
    return TeamFull.model_validate(
        team,
        update={
            "members": [
                UserForTeam.model_validate(member_link.member, update={"member_role": member_link.role})
                for member_link in team.member_links
            ]
        },
    )


@router.patch("/update/{team_id}")
def team_update(
        team_id: int,
        updates: TeamUpdate,
        authUserId=Depends(auth_handler.get_user),
        session=Depends(get_session)
) -> TeamFull:
    member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id, MemberTeamLink.user_id == authUserId)).first()
    if member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = updates.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(team, key, value)
    session.add(team)
    session.commit()
    session.refresh(team)
    return TeamFull.model_validate(
        team,
        update={
            "members": [
                UserForTeam.model_validate(member_link.member, update={"member_role": member_link.role})
                for member_link in team.member_links
            ]
        },
    )


@router.delete("/delete-team/{team_id}")
def team_delete(team_id: int, authUserId=Depends(auth_handler.get_user), session=Depends(get_session)):
    member_team_link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id, MemberTeamLink.user_id == authUserId)).first()
    if member_team_link is None:
        raise HTTPException(status_code=403, detail="User not available")
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}