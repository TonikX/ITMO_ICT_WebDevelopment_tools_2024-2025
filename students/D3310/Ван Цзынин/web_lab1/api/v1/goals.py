from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import FinancialGoal, User  # 从 models 包导入
from dependencies.database import get_session  # 依赖数据库会话

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=FinancialGoal)
def create_goal(goal: FinancialGoal, session: Session = Depends(get_session)):
    # 检查用户是否存在
    user = session.get(User, goal.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal