from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import Transaction, User, Category  # 从 models 包导入
from dependencies.database import get_session  # 依赖数据库会话

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=Transaction)
def create_transaction(transaction: Transaction, session: Session = Depends(get_session)):
    # 检查用户是否存在
    user = session.get(User, transaction.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查分类是否存在（可选）
    if transaction.category_id:
        category = session.get(Category, transaction.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction