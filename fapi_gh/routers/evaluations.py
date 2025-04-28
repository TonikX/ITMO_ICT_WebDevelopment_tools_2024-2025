from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from db.db import get_session
from models.models import (
    Evaluation, EvaluationBase,
    Submission, Challenge, User
)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/", response_model=Evaluation, status_code=status.HTTP_201_CREATED)
def create_evaluation(evaluation: EvaluationBase, session: Session = Depends(get_session)):
    """Добавление оценки для решения."""
    # Проверка существования решения
    submission = session.get(Submission, evaluation.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Решение не найдено")

    # Проверка существования судьи
    judge = session.get(User, evaluation.judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Судья не найден")

    # Проверка, не оценивал ли уже этот судья данное решение
    existing_evaluation = session.exec(
        select(Evaluation).where(
            Evaluation.submission_id == evaluation.submission_id,
            Evaluation.judge_id == evaluation.judge_id
        )
    ).first()

    if existing_evaluation:
        raise HTTPException(
            status_code=400,
            detail="Данный судья уже оценил это решение"
        )

    # Проверка диапазона оценки
    challenge = session.get(Challenge, submission.challenge_id)
    if evaluation.score < 0 or evaluation.score > challenge.max_score:
        raise HTTPException(
            status_code=400,
            detail=f"Оценка должна быть в диапазоне от 0 до {challenge.max_score}"
        )

    # Создание оценки
    db_evaluation = Evaluation.from_orm(evaluation)
    session.add(db_evaluation)
    session.commit()
    session.refresh(db_evaluation)
    return db_evaluation


@router.get("/", response_model=List[Evaluation])
def get_evaluations(
        skip: int = 0,
        limit: int = 100,
        submission_id: Optional[int] = None,
        judge_id: Optional[int] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        session: Session = Depends(get_session)
):
    """Получение списка оценок с возможностью фильтрации."""
    query = select(Evaluation)

    if submission_id:
        query = query.where(Evaluation.submission_id == submission_id)
    if judge_id:
        query = query.where(Evaluation.judge_id == judge_id)
    if min_score is not None:
        query = query.where(Evaluation.score >= min_score)
    if max_score is not None:
        query = query.where(Evaluation.score <= max_score)
    if date_from:
        query = query.where(Evaluation.evaluation_date >= date_from)
    if date_to:
        query = query.where(Evaluation.evaluation_date <= date_to)

    evaluations = session.exec(query.offset(skip).limit(limit)).all()
    return evaluations


@router.get("/{evaluation_id}", response_model=Evaluation)
def get_evaluation(evaluation_id: int, session: Session = Depends(get_session)):
    """Получение конкретной оценки по ID."""
    evaluation = session.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Оценка не найдена")
    return evaluation


@router.put("/{evaluation_id}", response_model=Evaluation)
def update_evaluation(
        evaluation_id: int,
        evaluation_data: EvaluationBase,
        session: Session = Depends(get_session)
):
    """Обновление данных оценки."""
    db_evaluation = session.get(Evaluation, evaluation_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Оценка не найдена")

    # Проверка диапазона оценки, если она изменилась
    if evaluation_data.score != db_evaluation.score:
        submission = session.get(Submission, db_evaluation.submission_id)
        challenge = session.get(Challenge, submission.challenge_id)
        if evaluation_data.score < 0 or evaluation_data.score > challenge.max_score:
            raise HTTPException(
                status_code=400,
                detail=f"Оценка должна быть в диапазоне от 0 до {challenge.max_score}"
            )

    evaluation_dict = evaluation_data.dict(exclude_unset=True)
    for key, value in evaluation_dict.items():
        setattr(db_evaluation, key, value)

    session.add(db_evaluation)
    session.commit()
    session.refresh(db_evaluation)
    return db_evaluation


@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evaluation(evaluation_id: int, session: Session = Depends(get_session)):
    """Удаление оценки."""
    db_evaluation = session.get(Evaluation, evaluation_id)
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Оценка не найдена")

    session.delete(db_evaluation)
    session.commit()
    return None


@router.get("/submission/{submission_id}", response_model=List[Evaluation])
def get_submission_evaluations(
        submission_id: int,
        session: Session = Depends(get_session)
):
    """Получение всех оценок для конкретного решения."""
    # Проверка существования решения
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Решение не найдено")

    query = select(Evaluation).where(Evaluation.submission_id == submission_id)
    evaluations = session.exec(query).all()
    return evaluations


@router.get("/judge/{judge_id}", response_model=List[Evaluation])
def get_judge_evaluations(
        judge_id: int,
        session: Session = Depends(get_session)
):
    """Получение всех оценок, сделанных конкретным судьей."""
    # Проверка существования судьи
    judge = session.get(User, judge_id)
    if not judge:
        raise HTTPException(status_code=404, detail="Судья не найден")

    query = select(Evaluation).where(Evaluation.judge_id == judge_id)
    evaluations = session.exec(query).all()
    return evaluations