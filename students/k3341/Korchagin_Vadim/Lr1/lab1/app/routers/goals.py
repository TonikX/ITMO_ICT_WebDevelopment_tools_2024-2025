from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from datetime import datetime

from app.db.connection import get_session
from app.models.finance_models import Goal, User
from app.schemas.finance_schemas import CreateGoal, ReadGoal, ReadGoalWithUser
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.post("/", response_model=ReadGoal)
def create_goal(goal_data: CreateGoal, session: Session = Depends(get_session)):
    user = session.get(User, goal_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goal = Goal(
        user_id=goal_data.user_id,
        title=goal_data.title,
        target_amount=goal_data.target_amount,
        deadline=goal_data.deadline,
        current_amount=goal_data.current_amount
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

@router.get("/", response_model=List[ReadGoal])
def get_all_goals(session: Session = Depends(get_session)):
    return session.exec(select(Goal)).all()

@router.get("/{goal_id}", response_model=ReadGoalWithUser)
def get_goal(goal_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Goal)
        .where(Goal.id == goal_id)
        .options(selectinload(Goal.user))
    )
    db_goal = session.exec(stmt).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal

@router.patch("/{goal_id}", response_model=ReadGoal)
def update_goal(goal_id: int, data: CreateGoal, session: Session = Depends(get_session)):
    db_goal = session.get(Goal, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_goal.user_id = data.user_id
    db_goal.title = data.title
    db_goal.target_amount = data.target_amount
    db_goal.deadline = data.deadline
    db_goal.current_amount = data.current_amount

    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, session: Session = Depends(get_session)):
    db_goal = session.get(Goal, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    session.delete(db_goal)
    session.commit()
    return {"ok": True}