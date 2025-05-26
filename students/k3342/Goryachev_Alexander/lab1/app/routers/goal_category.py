from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import GoalCategoryLink, Goal, Category, User
from app.connections import get_session
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/goal-category-links", tags=["GoalCategoryLinks"])


# Создание связи между целью и категорией
@router.post("/", response_model=GoalCategoryLink)
def create_goal_category_link(goal_category_link: GoalCategoryLink, session: Session = Depends(get_session),
                              user: User = Depends(get_current_user)):
    goal = session.get(Goal, goal_category_link.goal_id)
    category = session.get(Category, goal_category_link.category_id)

    if not goal or goal.user_id != user.id:
        raise HTTPException(status_code=404, detail="Goal not found or doesn't belong to the user")
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found or doesn't belong to the user")

    session.add(goal_category_link)
    session.commit()
    session.refresh(goal_category_link)
    return goal_category_link


@router.get("/", response_model=list[GoalCategoryLink])
def get_user_goal_category_links(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = select(GoalCategoryLink).join(Goal).where(Goal.user_id == user.id)
    return session.exec(statement).all()


@router.get("/{goal_id}/{category_id}", response_model=GoalCategoryLink)
def get_goal_category_link(goal_id: int, category_id: int, session: Session = Depends(get_session),
                           user: User = Depends(get_current_user)):
    goal_category_link = session.exec(select(GoalCategoryLink).where(GoalCategoryLink.goal_id == goal_id,
                                                                     GoalCategoryLink.category_id == category_id)).first()
    if not goal_category_link:
        raise HTTPException(status_code=404, detail="GoalCategoryLink not found")
    goal = session.get(Goal, goal_id)
    category = session.get(Category, category_id)
    if goal.user_id != user.id or category.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this link")
    return goal_category_link


@router.put("/{goal_id}/{category_id}", response_model=GoalCategoryLink)
def update_goal_category_link(goal_id: int, category_id: int, updated: GoalCategoryLink,
                              session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    goal_category_link = session.exec(select(GoalCategoryLink).where(GoalCategoryLink.goal_id == goal_id,
                                                                     GoalCategoryLink.category_id == category_id)).first()
    if not goal_category_link:
        raise HTTPException(status_code=404, detail="GoalCategoryLink not found")

    goal = session.get(Goal, goal_id)
    category = session.get(Category, category_id)
    if goal.user_id != user.id or category.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this link")

    # Обновление значений
    for field, value in updated.dict(exclude_unset=True).items():
        setattr(goal_category_link, field, value)

    session.add(goal_category_link)
    session.commit()
    session.refresh(goal_category_link)
    return goal_category_link


@router.delete("/{goal_id}/{category_id}")
def delete_goal_category_link(goal_id: int, category_id: int, session: Session = Depends(get_session),
                              user: User = Depends(get_current_user)):
    goal_category_link = session.exec(select(GoalCategoryLink).where(GoalCategoryLink.goal_id == goal_id,
                                                                     GoalCategoryLink.category_id == category_id)).first()
    if not goal_category_link:
        raise HTTPException(status_code=404, detail="GoalCategoryLink not found")

    goal = session.get(Goal, goal_id)
    category = session.get(Category, category_id)
    if goal.user_id != user.id or category.user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this link")

    session.delete(goal_category_link)
    session.commit()
    return {"ok": True}