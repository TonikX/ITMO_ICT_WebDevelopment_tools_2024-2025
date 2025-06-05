from fastapi import FastAPI, Depends, HTTPException, status, Form, APIRouter
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.connection import get_session
from app.models import (
    UserCreate, UserRead,
    CategoryCreate, CategoryRead,
    TransactionCreate, TransactionRead,
    BudgetCreate, BudgetRead,
    GoalCreate, GoalRead,
    NotificationCreate, NotificationRead
)
from app.tables import User, Category, Transaction, Budget, Goal, Notification, TransactionCategoryLink
from app.auth import get_current_user, encode_token
from app.hashing import get_password_hash, verify_password
from app.crud import (
    create_entity, get_entity, get_entities, delete_entity, get_user_by_credential
)

finance_router = APIRouter(prefix="/api", tags=["finance"])

@finance_router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    if get_user_by_credential(session, user.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if get_user_by_credential(session, user.email):
        raise HTTPException(status_code=409, detail="Email already exists")
    user_data = user.dict()
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    return create_entity(session, User, user_data)

@finance_router.post("/login")
def login(
        credential: str = Form(...),
        password: str = Form(...),
        session: Session = Depends(get_session)
):
    user = get_user_by_credential(session, credential)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": encode_token(user.id), "token_type": "bearer"}

@finance_router.get("/users/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@finance_router.post("/users/change-password")
def change_password(old_password: str = Form(...), new_password: str = Form(...),
                    session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid password")
    current_user.password_hash = get_password_hash(new_password)
    session.add(current_user)
    session.commit()
    return {"message": "Password updated"}

@finance_router.post("/categories", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    return create_entity(session, Category, category.dict())

@finance_router.get("/categories", response_model=list[CategoryRead])
def read_categories(session: Session = Depends(get_session)):
    return get_entities(session, Category)

@finance_router.delete("/categories/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    delete_entity(session, Category, category_id)
    return {"message": "Category deleted"}

@finance_router.post("/transactions", response_model=TransactionRead)
def create_transaction(transaction: TransactionCreate, session: Session = Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    data = transaction.dict()
    category_ids = data.pop("category_ids")
    data["user_id"] = current_user.id
    db_transaction = Transaction(**data)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    for category_id in category_ids:
        link = TransactionCategoryLink(transaction_id=db_transaction.id, category_id=category_id)
        session.add(link)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@finance_router.get("/transactions", response_model=list[TransactionRead])
def read_transactions(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    stmt = select(Transaction).where(Transaction.user_id == current_user.id).options(
        selectinload(Transaction.categories))
    transactions = session.exec(stmt).all()
    return transactions

@finance_router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session),
                       current_user: User = Depends(get_current_user)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    links = session.exec(
        select(TransactionCategoryLink).where(TransactionCategoryLink.transaction_id == transaction_id)).all()
    for link in links:
        session.delete(link)
    session.delete(transaction)
    session.commit()
    return {"message": "Transaction deleted"}

@finance_router.post("/budgets", response_model=BudgetRead)
def create_budget(budget: BudgetCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = budget.dict()
    data["user_id"] = current_user.id
    return create_entity(session, Budget, data)

@finance_router.get("/budgets", response_model=list[BudgetRead])
def read_budgets(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_entities(session, Budget, current_user.id)

@finance_router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    delete_entity(session, Budget, budget_id, user_id=current_user.id)
    return {"message": "Budget deleted"}

@finance_router.post("/goals", response_model=GoalRead)
def create_goal(goal: GoalCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = goal.dict()
    data["user_id"] = current_user.id
    return create_entity(session, Goal, data)

@finance_router.get("/goals", response_model=list[GoalRead])
def read_goals(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_entities(session, Goal, current_user.id)

@finance_router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    delete_entity(session, Goal, goal_id, user_id=current_user.id)
    return {"message": "Goal deleted"}

@finance_router.post("/notifications", response_model=NotificationRead)
def create_notification(notification: NotificationCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    data = notification.dict()
    data["user_id"] = current_user.id
    return create_entity(session, Notification, data)

@finance_router.get("/notifications", response_model=list[NotificationRead])
def read_notifications(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_entities(session, Notification, current_user.id)

@finance_router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    delete_entity(session, Notification, notification_id, user_id=current_user.id)
    return {"message": "Notification deleted"}