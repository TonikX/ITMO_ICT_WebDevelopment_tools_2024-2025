from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from db.db import get_session
from models.models import TeamMember, TeamMemberBase, TeamMemberResponse, Team, User, Hackathon

router = APIRouter(prefix="/team-members", tags=["team_members"])


@router.post("/", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(team_member: TeamMemberBase, session: Session = Depends(get_session)):
    """Добавление участника в команду."""
    # Проверка существования пользователя
    user = session.get(User, team_member.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Проверка существования команды
    team = session.get(Team, team_member.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    # Проверка, не состоит ли пользователь уже в этой команде
    existing_member = session.exec(
        select(TeamMember).where(
            TeamMember.user_id == team_member.user_id,
            TeamMember.team_id == team_member.team_id
        )
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="Пользователь уже является участником этой команды"
        )

    # Проверка максимального размера команды
    hackathon = session.get(Hackathon, team.hackathon_id)
    if hackathon.max_team_size:
        current_members_count = session.exec(
            select(TeamMember).where(TeamMember.team_id == team.id)
        ).all()
        if len(current_members_count) >= hackathon.max_team_size:
            raise HTTPException(
                status_code=400,
                detail=f"Превышен максимальный размер команды ({hackathon.max_team_size})"
            )

    # Добавление участника
    db_team_member = TeamMember.from_orm(team_member)
    session.add(db_team_member)
    session.commit()
    session.refresh(db_team_member)
    return db_team_member


@router.get("/", response_model=List[TeamMemberResponse])
def get_team_members(
        team_id: Optional[int] = None,
        user_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    """Получение списка участников команд с возможностью фильтрации."""
    query = select(TeamMember)

    if team_id:
        query = query.where(TeamMember.team_id == team_id)
    if user_id:
        query = query.where(TeamMember.user_id == user_id)
    if is_approved is not None:
        query = query.where(TeamMember.is_approved == is_approved)
    if role:
        query = query.where(TeamMember.role == role)

    team_members = session.exec(query.offset(skip).limit(limit)).all()
    return team_members


@router.get("/{member_id}", response_model=TeamMemberResponse)
def get_team_member(member_id: int, session: Session = Depends(get_session)):
    """Получение информации о конкретном участнике команды."""
    member = session.get(TeamMember, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Участник команды не найден")
    return member


@router.put("/{member_id}", response_model=TeamMemberResponse)
def update_team_member(
        member_id: int,
        member_data: TeamMemberBase,
        session: Session = Depends(get_session)
):
    """Обновление данных участника команды."""
    db_member = session.get(TeamMember, member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Участник команды не найден")

    member_dict = member_data.dict(exclude_unset=True)
    for key, value in member_dict.items():
        setattr(db_member, key, value)

    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member


@router.patch("/{member_id}/approve", response_model=TeamMemberResponse)
def approve_team_member(member_id: int, session: Session = Depends(get_session)):
    """Подтверждение участия в команде."""
    db_member = session.get(TeamMember, member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Участник команды не найден")

    db_member.is_approved = True
    session.add(db_member)
    session.commit()
    session.refresh(db_member)
    return db_member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(member_id: int, session: Session = Depends(get_session)):
    """Удаление участника из команды."""
    db_member = session.get(TeamMember, member_id)
    if not db_member:
        raise HTTPException(status_code=404, detail="Участник команды не найден")

    # Проверка, не является ли участник капитаном (нельзя удалить капитана)
    if db_member.role == "капитан":
        raise HTTPException(
            status_code=400,
            detail="Нельзя удалить капитана команды. Сначала назначьте нового капитана."
        )

    session.delete(db_member)
    session.commit()
    return None