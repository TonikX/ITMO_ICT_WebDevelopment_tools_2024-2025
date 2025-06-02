from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from typing import List
from db.connection import get_session
from models.models import User, Transaction, Category, Budget
from schemas.transaction import TransactionCreate, TransactionRead
from schemas.budget import BudgetCreate, BudgetRead
from schemas.category import CategoryCreate, CategoryRead
from schemas.user import UserCreate, UserRead, UserOut, Token, ChangePasswordRequest
from auth.auth import encode_jwt, decode_jwt, get_current_user

router = APIRouter()

# USERS
@router.post("/users", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[UserRead])
def get_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user

# TRANSACTIONS
@router.post("/transactions", response_model=TransactionRead)
def create_transaction(transaction: TransactionCreate, session: Session = Depends(get_session)):
    db_transaction = Transaction(**transaction.model_dump())
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@router.get("/transactions/{user_id}", response_model=List[TransactionRead])
def get_transactions_by_user(user_id: int, session: Session = Depends(get_session)):
    stmt = select(Transaction).where(Transaction.user_id == user_id)
    result = session.execute(stmt).all()
    return result

@router.patch("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, transaction: TransactionCreate, session: Session = Depends(get_session)):
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in transaction.model_dump(exclude_unset=True).items():
        setattr(db_transaction, key, value)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@router.get("/transaction/{transaction_id}/detailed")
def get_transaction_with_user(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.refresh(transaction, attribute_names=["user"])
    return {
        "id": transaction.id,
        "user_id": transaction.user_id,
        "user": {
            "id": transaction.user.id,
            "username": transaction.user.username
        }
    }

@router.delete("/transactions/{transaction_id}", response_model=TransactionRead)
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return transaction


# CATEGORIES
@router.post("/categories/", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = Category(**category.model_dump())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[CategoryRead])
def get_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

@router.patch("/categories/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in category.model_dump(exclude_unset=True).items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", response_model=CategoryRead)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return category

# BUDGETS
@router.post("/budgets/", response_model=BudgetRead)
def create_budget(budget: BudgetCreate, session: Session = Depends(get_session)):
    db_budget = Budget(**budget.model_dump())
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget

@router.get("/budgets/", response_model=List[BudgetRead])
def get_budgets(session: Session = Depends(get_session)):
    return session.exec(select(Budget)).all()

@router.patch("/budgets/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, budget: BudgetCreate, session: Session = Depends(get_session)):
    db_budget = session.get(Budget, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    for key, value in budget.model_dump(exclude_unset=True).items():
        setattr(db_budget, key, value)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget

@router.delete("/budgets/{budget_id}", response_model=BudgetRead)
def delete_budget(budget_id: int, session: Session = Depends(get_session)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(budget)
    session.commit()
    return budget


#AUTH
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        currency=user.currency
    )
    new_user.set_password(user.password)  # Хэшируем пароль перед сохранением

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = session.query(User).filter(User.email == user.email).first()
    if db_user is None or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": db_user.email,
        "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()
    }
    access_token = encode_jwt(payload)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user



def get_token_from_header(request: Request) -> str:
    """Извлекаем токен из заголовка Authorization"""
    auth = request.headers.get("Authorization")
    if auth is None or not auth.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Authorization header missing or invalid")
    return auth.split(" ")[1]

@router.post("/users/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Проверка текущего пароля
    if not current_user.verify_password(data.current_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Установка нового пароля
    current_user.set_password(data.new_password)
    session.commit()

    return {"message": "Password changed successfully"}
