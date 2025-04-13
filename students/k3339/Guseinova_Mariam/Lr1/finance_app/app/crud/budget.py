from sqlalchemy.orm import Session, joinedload
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate


def create_budget(db: Session, budget: BudgetCreate, user_id: int):
    db_budget = Budget(**budget.dict(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_user_budgets(db: Session, user_id: int):
    return (
        db.query(Budget)
        .filter(Budget.user_id == user_id)
        .options(joinedload(Budget.category))
        .all()
    )

def get_budget(db: Session, budget_id: int):
    return db.query(Budget).filter(Budget.budget_id == budget_id).first()

def update_budget(db: Session, budget_id: int, budget_data: BudgetUpdate):
    db_budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not db_budget:
        return None

    for key, value in budget_data.dict(exclude_unset=True).items():
        setattr(db_budget, key, value)

    db.commit()
    db.refresh(db_budget)
    return db_budget


def delete_budget(db: Session, budget_id: int):
    db_budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not db_budget:
        return False

    db.delete(db_budget)
    db.commit()
    return True