from sqlmodel import Session, select
from app.models.budget import Budget

def get_budget(session: Session, budget_id: int) -> Budget:
    statement = select(Budget).where(Budget.id == budget_id)
    return session.exec(statement).first()

def get_budgets(session: Session, skip: int = 0, limit: int = 100):
    statement = select(Budget).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_budget(session: Session, budget: Budget) -> Budget:
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

def update_budget(session: Session, budget: Budget) -> Budget:
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

def delete_budget(session: Session, budget: Budget):
    session.delete(budget)
    session.commit()
