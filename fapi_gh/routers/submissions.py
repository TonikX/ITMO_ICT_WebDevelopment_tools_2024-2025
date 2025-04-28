from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from db.db import get_session
from models.models import (
    Submission, SubmissionBase, SubmissionWithEvaluations,
    Team, Challenge, User
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("/", response_model=SubmissionWithEvaluations, status_code=status.HTTP_201_CREATED)
def create_submission(submission: SubmissionBase, session: Session = Depends(get_session)):
    """Создание нового решения/проекта."""
    # Проверка существования команды
    team = session.get(Team, submission.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    # Проверка существования задачи
    challenge = session.get(Challenge, submission.challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    # Проверка, что задача относится к тому же хакатону, что и команда
    if challenge.hackathon_id != team.hackathon_id:
        raise HTTPException(
            status_code=400,
            detail="Задача не относится к хакатону, в котором участвует команда"
        )

    # Проверка существования пользователя
    user = session.get(User, submission.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Создание решения
    db_submission = Submission.from_orm(submission)
    session.add(db_submission)
    session.commit()
    session.refresh(db_submission)
    return db_submission


@router.get("/", response_model=List[SubmissionWithEvaluations])
def get_submissions(
        skip: int = 0,
        limit: int = 100,
        team_id: Optional[int] = None,
        challenge_id: Optional[int] = None,
        user_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        session: Session = Depends(get_session)
):
    """Получение списка решений с возможностью фильтрации."""
    query = select(Submission)

    if team_id:
        query = query.where(Submission.team_id == team_id)
    if challenge_id:
        query = query.where(Submission.challenge_id == challenge_id)
    if user_id:
        query = query.where(Submission.user_id == user_id)
    if date_from:
        query = query.where(Submission.submission_date >= date_from)
    if date_to:
        query = query.where(Submission.submission_date <= date_to)

    submissions = session.exec(query.offset(skip).limit(limit)).all()
    return submissions


@router.get("/{submission_id}", response_model=SubmissionWithEvaluations)
def get_submission(submission_id: int, session: Session = Depends(get_session)):
    """Получение информации о конкретном решении."""
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Решение не найдено")
    return submission


@router.put("/{submission_id}", response_model=SubmissionWithEvaluations)
def update_submission(
        submission_id: int,
        submission_data: SubmissionBase,
        session: Session = Depends(get_session)
):
    """Обновление данных решения."""
    db_submission = session.get(Submission, submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Решение не найдено")

    submission_dict = submission_data.dict(exclude_unset=True)
    for key, value in submission_dict.items():
        setattr(db_submission, key, value)

    session.add(db_submission)
    session.commit()
    session.refresh(db_submission)
    return db_submission


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(submission_id: int, session: Session = Depends(get_session)):
    """Удаление решения."""
    db_submission = session.get(Submission, submission_id)
    if not db_submission:
        raise HTTPException(status_code=404, detail="Решение не найдено")

    session.delete(db_submission)
    session.commit()
    return None


@router.get("/team/{team_id}", response_model=List[SubmissionWithEvaluations])
def get_team_submissions(
        team_id: int,
        challenge_id: Optional[int] = None,
        session: Session = Depends(get_session)
):
    """Получение всех решений конкретной команды."""
    # Проверка существования команды
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")

    query = select(Submission).where(Submission.team_id == team_id)

    if challenge_id:
        query = query.where(Submission.challenge_id == challenge_id)

    submissions = session.exec(query).all()
    return submissions


@router.get("/challenge/{challenge_id}", response_model=List[SubmissionWithEvaluations])
def get_challenge_submissions(
        challenge_id: int,
        session: Session = Depends(get_session)
):
    """Получение всех решений для конкретной задачи."""
    # Проверка существования задачи
    challenge = session.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    query = select(Submission).where(Submission.challenge_id == challenge_id)
    submissions = session.exec(query).all()
    return submissions