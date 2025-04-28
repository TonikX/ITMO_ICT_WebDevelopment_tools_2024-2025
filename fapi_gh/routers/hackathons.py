from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from db.db import get_session
from models.models import Hackathon, HackathonBase, HackathonResponse, Team, TeamWithMembers

router = APIRouter(prefix="/hackathons", tags=["hackathons"])


@router.post("/", response_model=HackathonResponse, status_code=status.HTTP_201_CREATED)
def create_hackathon(hackathon: HackathonBase, session: Session = Depends(get_session)):
    """Создание нового хакатона."""
    db_hackathon = Hackathon.from_orm(hackathon)
    session.add(db_hackathon)
    session.commit()
    session.refresh(db_hackathon)
    return db_hackathon


@router.get("/", response_model=List[HackathonResponse])
def get_hackathons(
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        status: Optional[str] = None,
        is_online: Optional[bool] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None,
        session: Session = Depends(get_session)
):
    """Получение списка хакатонов с возможностью фильтрации."""
    query = select(Hackathon)

    if name:
        query = query.where(Hackathon.name.contains(name))
    if status:
        query = query.where(Hackathon.status == status)
    if is_online is not None:
        query = query.where(Hackathon.is_online == is_online)
    if start_date_from:
        query = query.where(Hackathon.start_date >= start_date_from)
    if start_date_to:
        query = query.where(Hackathon.start_date <= start_date_to)

    hackathons = session.exec(query.offset(skip).limit(limit)).all()
    return hackathons


@router.get("/{hackathon_id}", response_model=HackathonResponse)
def get_hackathon(hackathon_id: int, session: Session = Depends(get_session)):
    """Получение информации о хакатоне по ID."""
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Хакатон не найден")
    return hackathon


@router.put("/{hackathon_id}", response_model=HackathonResponse)
def update_hackathon(hackathon_id: int, hackathon_data: HackathonBase, session: Session = Depends(get_session)):
    """Обновление данных хакатона."""
    db_hackathon = session.get(Hackathon, hackathon_id)
    if not db_hackathon:
        raise HTTPException(status_code=404, detail="Хакатон не найден")

    hackathon_dict = hackathon_data.dict(exclude_unset=True)
    for key, value in hackathon_dict.items():
        setattr(db_hackathon, key, value)

    session.add(db_hackathon)
    session.commit()
    session.refresh(db_hackathon)
    return db_hackathon


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hackathon(hackathon_id: int, session: Session = Depends(get_session)):
    """Удаление хакатона."""
    db_hackathon = session.get(Hackathon, hackathon_id)
    if not db_hackathon:
        raise HTTPException(status_code=404, detail="Хакатон не найден")

    # Проверка наличия команд, связанных с хакатоном
    teams = session.exec(select(Team).where(Team.hackathon_id == hackathon_id)).all()
    if teams:
        raise HTTPException(
            status_code=400,
            detail="Невозможно удалить хакатон, так как с ним связаны команды"
        )

    session.delete(db_hackathon)
    session.commit()
    return None


@router.patch("/{hackathon_id}/status", response_model=HackathonResponse)
def update_hackathon_status(
        hackathon_id: int,
        status: str,
        session: Session = Depends(get_session)
):
    """Обновление статуса хакатона."""
    valid_statuses = ["upcoming", "active", "completed", "canceled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Некорректный статус. Допустимые значения: {', '.join(valid_statuses)}"
        )

    db_hackathon = session.get(Hackathon, hackathon_id)
    if not db_hackathon:
        raise HTTPException(status_code=404, detail="Хакатон не найден")

    db_hackathon.status = status
    session.add(db_hackathon)
    session.commit()
    session.refresh(db_hackathon)
    return db_hackathon


@router.get("/{hackathon_id}/teams", response_model=List[TeamWithMembers])
def get_hackathon_teams(
        hackathon_id: int,
        is_active: Optional[bool] = None,
        name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session)
):
    """Получение всех команд, участвующих в конкретном хакатоне."""
    # Проверка существования хакатона
    hackathon = session.get(Hackathon, hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Хакатон не найден")

    query = select(Team).where(Team.hackathon_id == hackathon_id)

    if is_active is not None:
        query = query.where(Team.is_active == is_active)
    if name:
        query = query.where(Team.name.contains(name))

    teams = session.exec(query.offset(skip).limit(limit)).all()
    return teams