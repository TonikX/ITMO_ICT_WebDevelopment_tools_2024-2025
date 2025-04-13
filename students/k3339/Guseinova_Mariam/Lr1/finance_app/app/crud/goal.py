from sqlalchemy.orm import Session
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalUpdate


def create_goal(db: Session, goal: GoalCreate, user_id: int):
    db_goal = Goal(**goal.dict(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_goal(db: Session, goal_id: int, goal_data: GoalUpdate):
    db_goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not db_goal:
        return None

    for key, value in goal_data.dict(exclude_unset=True).items():
        setattr(db_goal, key, value)

    db.commit()
    db.refresh(db_goal)
    return db_goal


def delete_goal(db: Session, goal_id: int):
    db_goal = db.query(Goal).filter(Goal.goal_id == goal_id).first()
    if not db_goal:
        return False

    db.delete(db_goal)
    db.commit()
    return True


def get_user_goals(db: Session, user_id: int):
    return db.query(Goal).filter(Goal.user_id == user_id).all()

def get_goal(db: Session, goal_id: int):
    return db.query(Goal).filter(Goal.goal_id == goal_id).first()