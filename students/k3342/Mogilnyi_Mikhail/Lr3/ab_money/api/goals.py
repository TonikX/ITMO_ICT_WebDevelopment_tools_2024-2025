from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from connection import get_session
from models import Goal
from schemas import GoalCreate, GoalRead
from api.auth import get_current_user
from models import User

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(
        goal_in: GoalCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_goal = Goal(**goal_in.dict(), user_id=current_user.id)
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal


@router.get("/", response_model=List[GoalRead])
def list_goals(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    goals = session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()
    return goals


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(
        goal_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_goal = session.get(Goal, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if db_goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this goal")

    return db_goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(
        goal_id: int,
        goal_in: GoalCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_goal = session.get(Goal, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if db_goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this goal")

    update_data = goal_in.dict(exclude_unset=True, exclude={"user_id"})
    for key, val in update_data.items():
        setattr(db_goal, key, val)

    db_goal.user_id = current_user.id

    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
        goal_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_goal = session.get(Goal, goal_id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if db_goal.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this goal")

    session.delete(db_goal)
    session.commit()
    return None
