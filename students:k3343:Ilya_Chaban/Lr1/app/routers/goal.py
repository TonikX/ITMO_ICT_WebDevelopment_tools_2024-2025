from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import select, Session
from typing import List

from app.connection import get_session
from app.models import Goal, GoalDefault

router = APIRouter()

@router.post("/goal")
def create_goal(goal_data: GoalDefault, session: Session = Depends(get_session)):
    goal = Goal.model_validate(goal_data)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return {"status": 200, "data": goal}


@router.get("/goal_list", response_model=List[Goal])
def get_goals(session: Session = Depends(get_session)):
    return session.exec(select(Goal)).all()


@router.get("/goal/{goal_id}", response_model=Goal)
def get_goal_by_id(goal_id: int, session: Session = Depends(get_session)):
    goal = session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/goal/delete/{goal_id}")
def delete_goal(goal_id: int, session: Session = Depends(get_session)):
    goal = session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    session.delete(goal)
    session.commit()
    return {"status": "OK"}


@router.put("/goal/{goal_id}")
def update_goal(goal_id: int, goal_data: GoalDefault, session: Session = Depends(get_session)):
    goal = session.get(Goal, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    for key, value in goal_data.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return {"status": "OK", "data": goal}
