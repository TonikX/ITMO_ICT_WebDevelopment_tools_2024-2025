from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.connection import get_session
from app.auth import get_current_user, encode_token
from app.crud import get_user_by_credential, create_entity, get_entity, get_entities, delete_entity, create_user, get_categories_with_transactions, get_category_with_transactions
from app.models import (
    UserCreate, UserRead, LoginRequest, LoginResponse, CategoryCreate, CategoryRead, 
    TransactionCreate, TransactionRead, BudgetCreate, BudgetRead,
    GoalCreate, GoalRead, NotificationCreate, NotificationRead, CategoryReadWithTransactions
)
from app.tables import User, Category, Transaction, Budget, Goal, Notification
from app.hashing import verify_password

router = APIRouter()
    
@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, user)

@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    user = get_user_by_credential(session, login_data.username)
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
    
    token = encode_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserRead])
def read_users(session: Session = Depends(get_session)):
    return get_entities(session, User)

@router.post("/categories", response_model=CategoryRead)
def create_category(category: CategoryCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    category_data = category.dict()
    category_data["user_id"] = current_user.id
    return create_entity(session, Category, category_data)

@router.get("/categories", response_model=list[CategoryRead])
def read_categories(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Category, current_user.id)

@router.get("/categories/with-transactions", response_model=list[CategoryReadWithTransactions])
def read_categories_with_transactions(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    categories = get_categories_with_transactions(session, current_user.id)
    return categories

@router.get("/categories/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Category, category_id, current_user.id)

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Category, category_id, current_user.id)
    return {"message": "Category deleted"}

@router.post("/transactions", response_model=TransactionRead)
def create_transaction(transaction: TransactionCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    transaction_data = transaction.dict()
    transaction_data["user_id"] = current_user.id
    return create_entity(session, Transaction, transaction_data)

@router.get("/transactions", response_model=list[TransactionRead])
def read_transactions(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Transaction, current_user.id)

@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Transaction, transaction_id, current_user.id)

@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Transaction, transaction_id, current_user.id)
    return {"message": "Transaction deleted"}

@router.post("/budgets", response_model=BudgetRead)
def create_budget(budget: BudgetCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    budget_data = budget.dict()
    budget_data["user_id"] = current_user.id
    return create_entity(session, Budget, budget_data)

@router.get("/budgets", response_model=list[BudgetRead])
def read_budgets(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Budget, current_user.id)

@router.get("/budgets/{budget_id}", response_model=BudgetRead)
def read_budget(budget_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Budget, budget_id, current_user.id)

@router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Budget, budget_id, current_user.id)
    return {"message": "Budget deleted"}

@router.post("/goals", response_model=GoalRead)
def create_goal(goal: GoalCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    goal_data = goal.dict()
    goal_data["user_id"] = current_user.id
    return create_entity(session, Goal, goal_data)

@router.get("/goals", response_model=list[GoalRead])
def read_goals(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Goal, current_user.id)

@router.get("/goals/{goal_id}", response_model=GoalRead)
def read_goal(goal_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Goal, goal_id, current_user.id)

@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Goal, goal_id, current_user.id)
    return {"message": "Goal deleted"}

@router.post("/notifications", response_model=NotificationRead)
def create_notification(notification: NotificationCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    notification_data = notification.dict()
    notification_data["user_id"] = current_user.id
    return create_entity(session, Notification, notification_data)

@router.get("/notifications", response_model=list[NotificationRead])
def read_notifications(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Notification, current_user.id)

@router.get("/notifications/{notification_id}", response_model=NotificationRead)
def read_notification(notification_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Notification, notification_id, current_user.id)

@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Notification, notification_id, current_user.id)
    return {"message": "Notification deleted"}