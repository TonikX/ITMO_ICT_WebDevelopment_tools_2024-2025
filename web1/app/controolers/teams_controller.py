from fastapi import HTTPException
from sqlmodel import select, Session
from sqlalchemy import exc

from app.models import Team, User, TeamFull, TeamCreate, TeamUpdate, MemberTeamLink, UserForTeam


def get_all_teams(session: Session):
    return session.exec(select(Team)).all()


def get_team_by_id(team_id: int, session: Session):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamFull.model_validate(
        team,
        update={
            "members": [
                UserForTeam.model_validate(link.member, update={"member_role": link.role})
                for link in team.member_links
            ]
        },
    )


def create_team(team_data: TeamCreate, auth_user_id: int, session: Session):
    auth_user = session.get(User, auth_user_id)
    if not auth_user:
        raise HTTPException(status_code=403, detail="User not found")

    team = Team.model_validate(team_data)
    session.add(team)
    session.commit()
    session.refresh(team)

    member_link = MemberTeamLink(team_id=team.id, user_id=auth_user_id)
    session.add(member_link)
    session.commit()
    session.refresh(team)

    return get_team_by_id(team.id, session)


def add_member(team_id: int, user_id: int, role: str | None, auth_user_id: int, session: Session):
    if not is_user_in_team(team_id, auth_user_id, session):
        raise HTTPException(status_code=403, detail="User not available")

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    link = MemberTeamLink(team_id=team_id, user_id=user_id, role=role)
    session.add(link)

    try:
        session.commit()
    except exc.IntegrityError:
        raise HTTPException(status_code=400, detail="Member already exists")

    session.refresh(team)
    return get_team_by_id(team_id, session)


def delete_member(team_id: int, user_id: int, auth_user_id: int, session: Session):
    if not is_user_in_team(team_id, auth_user_id, session):
        raise HTTPException(status_code=403, detail="User not available")

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    link = session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id,
        MemberTeamLink.user_id == user_id
    )).first()

    if not link:
        raise HTTPException(status_code=404, detail="User not found in team")

    session.delete(link)
    session.commit()

    session.refresh(team)
    return get_team_by_id(team_id, session)


def update_team(team_id: int, updates: TeamUpdate, auth_user_id: int, session: Session):
    if not is_user_in_team(team_id, auth_user_id, session):
        raise HTTPException(status_code=403, detail="User not available")

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)

    session.add(team)
    session.commit()
    session.refresh(team)

    return get_team_by_id(team_id, session)


def delete_team(team_id: int, auth_user_id: int, session: Session):
    if not is_user_in_team(team_id, auth_user_id, session):
        raise HTTPException(status_code=403, detail="User not available")

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    session.delete(team)
    session.commit()
    return {"ok": True}


def is_user_in_team(team_id: int, user_id: int, session: Session) -> bool:
    return session.scalars(select(MemberTeamLink).where(
        MemberTeamLink.team_id == team_id,
        MemberTeamLink.user_id == user_id
    )).first() is not None
