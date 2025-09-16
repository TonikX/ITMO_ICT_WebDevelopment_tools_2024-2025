from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from db.connection import init_db, get_session
from models.tables import User, Category, Transaction, Budget, Goal, Notification
from models.models import (
    UserCreate, UserRead, CategoryCreate, CategoryRead, TransactionCreate, TransactionRead,
    BudgetCreate, BudgetRead, GoalCreate, GoalRead, NotificationCreate, NotificationRead, UserReadWithRelations, CategoryReadWithTransactions
)
from crud.crud import create_entity, get_entity, get_entities, delete_entity, create_user, get_user_by_credential, get_user_with_relations, get_category_with_transactions, get_categories_with_transactions
from services.auth import get_current_user, encode_token, security
from services.hashing import verify_password

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def hello():
    return "Welcome to Personal Finance Service"

@app.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    return create_user(session, user)

@app.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    user = get_user_by_credential(session, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = encode_token(user.id)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users/me/with-relations", response_model=UserReadWithRelations)
def read_user_with_relations(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    user = get_user_with_relations(session, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=list[UserRead])
def read_users(session: Session = Depends(get_session)):
    return get_entities(session, User)

@app.post("/categories", response_model=CategoryRead)
def create_category(category: CategoryCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    category_data = category.dict()
    category_data["user_id"] = current_user.id
    return create_entity(session, Category, category_data)

@app.get("/categories", response_model=list[CategoryRead])
def read_categories(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Category, current_user.id)

@app.get("/categories/with-transactions", response_model=list[CategoryReadWithTransactions])
def read_categories_with_transactions(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    categories = get_categories_with_transactions(session, current_user.id)
    return categories

@app.get("/categories/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Category, category_id, current_user.id)

@app.get("/categories/{category_id}/with-transactions", response_model=CategoryReadWithTransactions)
def read_category_with_transactions(category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    category = get_category_with_transactions(session, category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Category, category_id, current_user.id)
    return {"message": "Category deleted"}

@app.post("/transactions", response_model=TransactionRead)
def create_transaction(transaction: TransactionCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    transaction_data = transaction.dict()
    transaction_data["user_id"] = current_user.id
    return create_entity(session, Transaction, transaction_data)

@app.get("/transactions", response_model=list[TransactionRead])
def read_transactions(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Transaction, current_user.id)

@app.get("/transactions/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Transaction, transaction_id, current_user.id)

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Transaction, transaction_id, current_user.id)
    return {"message": "Transaction deleted"}

@app.post("/budgets", response_model=BudgetRead)
def create_budget(budget: BudgetCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    budget_data = budget.dict()
    budget_data["user_id"] = current_user.id
    return create_entity(session, Budget, budget_data)

@app.get("/budgets", response_model=list[BudgetRead])
def read_budgets(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Budget, current_user.id)

@app.get("/budgets/{budget_id}", response_model=BudgetRead)
def read_budget(budget_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Budget, budget_id, current_user.id)

@app.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Budget, budget_id, current_user.id)
    return {"message": "Budget deleted"}

@app.post("/goals", response_model=GoalRead)
def create_goal(goal: GoalCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    goal_data = goal.dict()
    goal_data["user_id"] = current_user.id
    return create_entity(session, Goal, goal_data)

@app.get("/goals", response_model=list[GoalRead])
def read_goals(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Goal, current_user.id)

@app.get("/goals/{goal_id}", response_model=GoalRead)
def read_goal(goal_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Goal, goal_id, current_user.id)

@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Goal, goal_id, current_user.id)
    return {"message": "Goal deleted"}

@app.post("/notifications", response_model=NotificationRead)
def create_notification(notification: NotificationCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    notification_data = notification.dict()
    notification_data["user_id"] = current_user.id
    return create_entity(session, Notification, notification_data)

@app.get("/notifications", response_model=list[NotificationRead])
def read_notifications(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entities(session, Notification, current_user.id)

@app.get("/notifications/{notification_id}", response_model=NotificationRead)
def read_notification(notification_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return get_entity(session, Notification, notification_id, current_user.id)

@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    delete_entity(session, Notification, notification_id, current_user.id)
    return {"message": "Notification deleted"}