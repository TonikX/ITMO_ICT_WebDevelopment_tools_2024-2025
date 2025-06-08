from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import User  # 从 models 包导入
from dependencies.database import get_session  # 依赖数据库会话

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    # 检查用户名/邮箱是否已存在
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    session.add(user)
    session.commit()
    session.refresh(user)
    return user