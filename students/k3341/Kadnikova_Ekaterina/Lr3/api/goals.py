from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from connection import get_session
from models.goal import Goal
from models.transaction import Transaction
from models.user import User
from schemas.goal import GoalRead, GoalCreate, GoalUpdate, TransactionRead
from api.auth import get_current_user

router = APIRouter()

@router.post("/goals/", response_model=GoalRead)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_goal = Goal(**goal.dict())
    db_goal.user_id = current_user.id

    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@router.get("/goals/", response_model=list[GoalRead])
def get_goals(db: Session = Depends(get_session)):
    return db.query(Goal).all()

@router.get("/goals/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int, db: Session = Depends(get_session)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Not found")
    return goal


@router.put("/goals/{goal_id}", response_model=GoalRead)
def update_goal(
        goal_id: int,
        goal_update: GoalUpdate,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this goal")

    if goal_update.name:
        goal.name = goal_update.name
    if goal_update.target_amount is not None:
        goal.target_amount = goal_update.target_amount
    if goal_update.description:
        goal.description = goal_update.description

    db.commit()
    db.refresh(goal)
    return goal

@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_session)):
    goal = db.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(goal)
    db.commit()
    return {"ok": True}


@router.get("/goals/{goal_id}/details", response_model=GoalRead)
def get_goal_detail(goal_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal.due_date is None:
        goal.due_date = datetime(2025, 12, 31)

    transactions = db.query(Transaction).filter(
        Transaction.linked_object_type == "goal",
        Transaction.linked_object_id == goal.id
    ).all()

    transactions_serialized = [TransactionRead.from_orm(transaction) for transaction in transactions]

    return {
        "id": goal.id,
        "user_id": goal.user_id,
        "title": goal.title,
        "target_amount": goal.target_amount,
        "created_at": goal.created_at,
        "due_date": goal.due_date,
        "transactions": transactions_serialized
    }