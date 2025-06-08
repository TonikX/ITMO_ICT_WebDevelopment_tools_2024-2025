from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import Budget, User  # 从 models 包导入
from dependencies.database import get_session  # 依赖数据库会话

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/", response_model=Budget)
def create_budget(budget: Budget, session: Session = Depends(get_session)):
    # 检查用户是否存在
    user = session.get(User, budget.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget