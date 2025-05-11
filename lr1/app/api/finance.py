from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app.schemas.finance import (
    AccountCreate, AccountOut,
    TransactionCreate, TransactionOut,
    CategoryCreate, CategoryOut,
    BudgetCreate, BudgetOut,
    GoalCreate, GoalOut,
    ExpenseAnalysisOut, BudgetNotificationOut,
    NotificationOut, DashboardSummary, SpendingTrend
)
from app.crud.finance import (
    create_account, get_accounts, get_account, update_account, delete_account,
    create_transaction, get_transactions, get_transaction, update_transaction, delete_transaction,
    create_category, get_categories, update_category, delete_category,
    create_budget, get_budgets, update_budget, delete_budget,
    create_goal, get_goals, update_goal, delete_goal,
    get_expense_analysis,
    get_notifications, get_dashboard_summary, get_spending_trends
)
from app.api.auth import get_current_user
from app.models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/accounts", response_model=AccountOut)
def create_account_endpoint(account: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AccountOut:
    return create_account(db, account, current_user.id)

@router.get("/accounts", response_model=List[AccountOut])
def read_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[AccountOut]:
    return get_accounts(db, current_user.id)

@router.get("/accounts/{account_id}", response_model=AccountOut)
def read_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AccountOut:
    db_account = get_account(db, account_id, current_user.id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.put("/accounts/{account_id}", response_model=AccountOut)
def update_account_endpoint(account_id: int, account: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> AccountOut:
    db_account = update_account(db, account_id, account, current_user.id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.delete("/accounts/{account_id}")
def delete_account_endpoint(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_account(db, account_id, current_user.id):
        raise HTTPException(status_code=404, detail="Account not found")
    return {"detail": "Account deleted"}

@router.post("/transactions", response_model=TransactionOut)
def create_transaction_endpoint(transaction: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TransactionOut:
    try:
        return create_transaction(db, transaction, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions", response_model=List[TransactionOut])
def read_transactions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[TransactionOut]:
    return get_transactions(db, current_user.id)

@router.get("/transactions/{transaction_id}", response_model=TransactionOut)
def read_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TransactionOut:
    db_transaction = get_transaction(db, transaction_id, current_user.id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.put("/transactions/{transaction_id}", response_model=TransactionOut)
def update_transaction_endpoint(transaction_id: int, transaction: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TransactionOut:
    try:
        db_transaction = update_transaction(db, transaction_id, transaction, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.delete("/transactions/{transaction_id}")
def delete_transaction_endpoint(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_transaction(db, transaction_id, current_user.id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "Transaction deleted"}

@router.post("/categories", response_model=CategoryOut)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CategoryOut:
    return create_category(db, category)

@router.get("/categories", response_model=List[CategoryOut])
def read_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[CategoryOut]:
    return get_categories(db)

@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category_endpoint(category_id: int, category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CategoryOut:
    db_category = update_category(db, category_id, category)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.delete("/categories/{category_id}")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"detail": "Category deleted"}

@router.post("/budgets", response_model=BudgetOut)
def create_budget_endpoint(budget: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> BudgetOut:
    try:
        return create_budget(db, budget, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/budgets", response_model=List[BudgetOut])
def read_budgets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[BudgetOut]:
    return get_budgets(db, current_user.id)

@router.put("/budgets/{budget_id}", response_model=BudgetOut)
def update_budget_endpoint(budget_id: int, budget: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> BudgetOut:
    try:
        db_budget = update_budget(db, budget_id, budget, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.delete("/budgets/{budget_id}")
def delete_budget_endpoint(budget_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_budget(db, budget_id, current_user.id):
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"detail": "Budget deleted"}

@router.post("/goals", response_model=GoalOut)
def create_goal_endpoint(goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> GoalOut:
    return create_goal(db, goal, current_user.id)

@router.get("/goals", response_model=List[GoalOut])
def read_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[GoalOut]:
    return get_goals(db, current_user.id)

@router.put("/goals/{goal_id}", response_model=GoalOut)
def update_goal_endpoint(goal_id: int, goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> GoalOut:
    db_goal = update_goal(db, goal_id, goal, current_user.id)
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db_goal

@router.delete("/goals/{goal_id}")
def delete_goal_endpoint(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not delete_goal(db, goal_id, current_user.id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"detail": "Goal deleted"}

@router.get("/analysis/expenses", response_model=List[ExpenseAnalysisOut])
def expense_analysis(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[ExpenseAnalysisOut]:
    analysis = get_expense_analysis(db, current_user.id)
    return analysis

@router.get("/notifications", response_model=List[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[NotificationOut]:
    return get_notifications(db, current_user.id)

@router.get("/dashboard", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DashboardSummary:
    summary = get_dashboard_summary(db, current_user.id)
    return summary

@router.get("/trends/spending", response_model=List[SpendingTrend])
def spending_trends(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> List[SpendingTrend]:
    trends = get_spending_trends(db, current_user.id)
    return trends
