from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.goal import create_goal, update_goal, delete_goal, get_user_goals, get_goal
from app.schemas.goal import GoalCreate, GoalOut, GoalUpdate
from app.database import SessionLocal
from app.auth.deps import get_db, get_current_user
from common.models.user import User
from common.models.goal import Goal

router = APIRouter(tags=["Goals"])


@router.post("/goals", response_model=GoalOut)
def create_new_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_goal(db, goal, current_user.user_id)

@router.get("/goals/me", response_model=list[GoalOut])
def get_my_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_goals(db, current_user.user_id)

@router.get("/goals/{goal_id}", response_model=GoalOut)
def get_single_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_goal = get_goal(db, goal_id)
    if not db_goal or db_goal.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal

@router.put("/goals/{goal_id}", response_model=GoalOut)
def update_existing_goal(
        goal_id: int,
        goal_data: GoalUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not db_goal or db_goal.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Goal not found")

    return update_goal(db, goal_id, goal_data)


@router.delete("/goals/{goal_id}")
def delete_existing_goal(
        goal_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not db_goal or db_goal.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Goal not found")

    delete_goal(db, goal_id)
    return {"msg": "Goal deleted"}