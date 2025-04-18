from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Goal, GoalCategoryLink, Category, User
from app.connections import get_session
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.post("/", response_model=Goal)
def create_goal(goal: Goal, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    goal.user_id = user.id

    # Проверка категорий
    for category in goal.categories:
        db_category = session.get(Category, category.id)
        if not db_category or db_category.user_id != user.id:
            raise HTTPException(status_code=400, detail="Invalid category for this user")

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

@router.get("/", response_model=list[Goal])
def get_goals(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = select(Goal).where(Goal.user_id == user.id)
    return session.exec(statement).all()

@router.get("/{goal_id}", response_model=Goal)
def get_goal(goal_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@router.put("/{goal_id}", response_model=Goal)
def update_goal(goal_id: int, updated: Goal, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    # если переданы категории — заменим связи
    if updated.categories:
        for category in updated.categories:
            db_category = session.get(Category, category.id)
            if not db_category or db_category.user_id != user.id:
                raise HTTPException(status_code=400, detail="Invalid category for this user")
        goal.categories = updated.categories

    for field, value in updated.dict(exclude_unset=True, exclude={"categories"}).items():
        setattr(goal, field, value)

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    session.delete(goal)
    session.commit()
    return {"ok": True}