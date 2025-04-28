from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional

from db.db import get_session
from models.models import Challenge, ChallengeBase, ChallengeResponse, Hackathon

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.post("/", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_challenge(challenge: ChallengeBase, session: Session = Depends(get_session)):
    """Создание новой задачи для хакатона."""
    # Проверка существования хакатона
    hackathon = session.get(Hackathon, challenge.hackathon_id)
    if not hackathon:
        raise HTTPException(status_code=404, detail="Хакатон не найден")

    # Создание задачи
    db_challenge = Challenge.from_orm(challenge)
    session.add(db_challenge)
    session.commit()
    session.refresh(db_challenge)
    return db_challenge


@router.get("/", response_model=List[ChallengeResponse])
def get_challenges(
        skip: int = 0,
        limit: int = 100,
        hackathon_id: Optional[int] = None,
        title: Optional[str] = None,
        session: Session = Depends(get_session)
):
    """Получение списка задач с возможностью фильтрации."""
    query = select(Challenge)

    if hackathon_id:
        query = query.where(Challenge.hackathon_id == hackathon_id)
    if title:
        query = query.where(Challenge.title.contains(title))

    challenges = session.exec(query.offset(skip).limit(limit)).all()
    return challenges


@router.get("/{challenge_id}", response_model=ChallengeResponse)
def get_challenge(challenge_id: int, session: Session = Depends(get_session)):
    """Получение информации о конкретной задаче."""
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return challenge


@router.put("/{challenge_id}", response_model=ChallengeResponse)
def update_challenge(
        challenge_id: int,
        challenge_data: ChallengeBase,
        session: Session = Depends(get_session)
):
    """Обновление данных задачи."""
    db_challenge = session.get(Challenge, challenge_id)
    if not db_challenge:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Проверка существования хакатона
    if challenge_data.hackathon_id != db_challenge.hackathon_id:
        hackathon = session.get(Hackathon, challenge_data.hackathon_id)
        if not hackathon:
            raise HTTPException(status_code=404, detail="Хакатон не найден")

    challenge_dict = challenge_data.dict(exclude_unset=True)
    for key, value in challenge_dict.items():
        setattr(db_challenge, key, value)

    session.add(db_challenge)
    session.commit()
    session.refresh(db_challenge)
    return db_challenge


@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(challenge_id: int, session: Session = Depends(get_session)):
    """Удаление задачи."""
    db_challenge = session.get(Challenge, challenge_id)
    if not db_challenge:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    session.delete(db_challenge)
    session.commit()
    return None