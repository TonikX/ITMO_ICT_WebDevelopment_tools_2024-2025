import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Account, Transaction, Category, TransactionCategory, Budget, Goal, Notification, TransactionType
from app.schemas.finance import AccountCreate, TransactionCreate, CategoryCreate, BudgetCreate, GoalCreate

def create_account(db: Session, account: AccountCreate, user_id: int):
    db_account = Account(user_id=user_id, name=account.name, balance=account.balance)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session, user_id: int):
    return db.query(Account).filter(Account.user_id == user_id).all()

def get_account(db: Session, account_id: int, user_id: int):
    return db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()

def update_account(db: Session, account_id: int, account_data: AccountCreate, user_id: int):
    db_account = get_account(db, account_id, user_id)
    if db_account:
        db_account.name = account_data.name
        db_account.balance = account_data.balance
        db.commit()
        db.refresh(db_account)
    return db_account

def delete_account(db: Session, account_id: int, user_id: int) -> bool:
    db_account = get_account(db, account_id, user_id)
    if db_account:
        db.delete(db_account)
        db.commit()
        return True
    return False

def check_budget_exceedance(db: Session, user_id: int, category_id: int):
    budgets = db.query(Budget).filter(Budget.user_id == user_id, Budget.category_id == category_id).all()
    for budget in budgets:
        if budget.start_date and budget.end_date:
            total_spent = db.query(func.sum(TransactionCategory.allocated_amount))\
                .join(Transaction, Transaction.id == TransactionCategory.transaction_id)\
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.expense,
                    TransactionCategory.category_id == category_id,
                    Transaction.date >= budget.start_date,
                    Transaction.date <= budget.end_date
                ).scalar() or 0.0
            if total_spent > budget.limit_amount:
                category = db.query(Category).filter(Category.id == category_id).first()
                title = "Budget Exceeded"
                message = f"Budget exceeded for category '{category.name}'. Limit: {budget.limit_amount}, Spent: {total_spent}"
                create_notification(db, user_id, title, message)

def create_transaction(db: Session, transaction: TransactionCreate, user_id: int):
    db_account = get_account(db, transaction.account_id, user_id)
    if not db_account:
        raise ValueError("Account not found")
    for tc in transaction.categories:
        db_category = db.query(Category).filter(Category.id == tc.category_id).first()
        if not db_category:
            raise ValueError(f"Category with id {tc.category_id} not found")
    db_transaction = Transaction(
        user_id=user_id,
        account_id=transaction.account_id,
        amount=transaction.amount,
        date=transaction.date if transaction.date else datetime.date.today(),
        description=transaction.description,
        type=transaction.type
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    for tc in transaction.categories:
        db_tc = TransactionCategory(
            transaction_id=db_transaction.id,
            category_id=tc.category_id,
            allocated_amount=tc.allocated_amount
        )
        db.add(db_tc)
    db.commit()
    db.refresh(db_transaction)
    for tc in transaction.categories:
        check_budget_exceedance(db, user_id, tc.category_id)
    return db_transaction

def get_transactions(db: Session, user_id: int):
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def get_transaction(db: Session, transaction_id: int, user_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user_id).first()

def update_transaction(db: Session, transaction_id: int, transaction_data: TransactionCreate, user_id: int):
    db_transaction = get_transaction(db, transaction_id, user_id)
    if db_transaction:
        db_account = get_account(db, transaction_data.account_id, user_id)
        if not db_account:
            raise ValueError("Account not found")
        db_transaction.account_id = transaction_data.account_id
        db_transaction.amount = transaction_data.amount
        db_transaction.date = transaction_data.date if transaction_data.date else db_transaction.date
        db_transaction.description = transaction_data.description
        db_transaction.type = transaction_data.type
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
    db_transaction = get_transaction(db, transaction_id, user_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False

def create_category(db: Session, category: CategoryCreate):
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session):
    return db.query(Category).all()

def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def update_category(db: Session, category_id: int, category_data: CategoryCreate):
    db_category = get_category(db, category_id)
    if db_category:
        db_category.name = category_data.name
        db_category.description = category_data.description
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
        return True
    return False

def create_budget(db: Session, budget: BudgetCreate, user_id: int):
    db_category = get_category(db, budget.category_id)
    if not db_category:
        raise ValueError("Category not found")
    db_budget = Budget(
        user_id=user_id,
        category_id=budget.category_id,
        period=budget.period,
        limit_amount=budget.limit_amount,
        start_date=budget.start_date,
        end_date=budget.end_date
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets(db: Session, user_id: int):
    return db.query(Budget).filter(Budget.user_id == user_id).all()

def get_budget(db: Session, budget_id: int, user_id: int):
    return db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()

def update_budget(db: Session, budget_id: int, budget_data: BudgetCreate, user_id: int):
    db_budget = get_budget(db, budget_id, user_id)
    if db_budget:
        db_category = get_category(db, budget_data.category_id)
        if not db_category:
            raise ValueError("Category not found")
        db_budget.category_id = budget_data.category_id
        db_budget.period = budget_data.period
        db_budget.limit_amount = budget_data.limit_amount
        db_budget.start_date = budget_data.start_date
        db_budget.end_date = budget_data.end_date
        db.commit()
        db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int, user_id: int) -> bool:
    db_budget = get_budget(db, budget_id, user_id)
    if db_budget:
        db.delete(db_budget)
        db.commit()
        return True
    return False

def create_goal(db: Session, goal: GoalCreate, user_id: int):
    db_goal = Goal(
        user_id=user_id,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        due_date=goal.due_date
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user_id: int):
    return db.query(Goal).filter(Goal.user_id == user_id).all()

def get_goal(db: Session, goal_id: int, user_id: int):
    return db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()

def update_goal(db: Session, goal_id: int, goal_data: GoalCreate, user_id: int):
    db_goal = get_goal(db, goal_id, user_id)
    if db_goal:
        db_goal.name = goal_data.name
        db_goal.target_amount = goal_data.target_amount
        db_goal.current_amount = goal_data.current_amount
        db_goal.due_date = goal_data.due_date
        db.commit()
        db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int, user_id: int) -> bool:
    db_goal = get_goal(db, goal_id, user_id)
    if db_goal:
        db.delete(db_goal)
        db.commit()
        return True
    return False

def get_expense_analysis(db: Session, user_id: int):
    analysis = (
       db.query(
         Category.name,
         func.sum(TransactionCategory.allocated_amount).label("total_expense")
       )
       .join(TransactionCategory, TransactionCategory.category_id == Category.id)
       .join(Transaction, Transaction.id == TransactionCategory.transaction_id)
       .filter(Transaction.user_id == user_id, Transaction.type == TransactionType.expense)
       .group_by(Category.name)
       .all()
    )
    return [{"category": row[0], "total_expense": row[1]} for row in analysis]

def create_notification(db: Session, user_id: int, title: str, message: str):
    notification = Notification(user_id=user_id, title=title, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

def get_dashboard_summary(db: Session, user_id: int):
    total_income = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user_id, Transaction.type == TransactionType.income).scalar() or 0.0
    total_expense = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id == user_id, Transaction.type == TransactionType.expense).scalar() or 0.0
    net_savings = total_income - total_expense
    return {"total_income": total_income, "total_expense": total_expense, "net_savings": net_savings}

def get_spending_trends(db: Session, user_id: int):
    trends = db.query(func.to_char(Transaction.date, 'YYYY-MM').label('month'),
                      func.sum(Transaction.amount).label('total_expense'))\
               .filter(Transaction.user_id == user_id, Transaction.type == TransactionType.expense)\
               .group_by('month').order_by('month').all()
    return [{"month": row[0], "total_expense": row[1]} for row in trends]
