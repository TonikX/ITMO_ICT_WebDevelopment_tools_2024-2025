from sqlmodel import Session, select
from fastapi import HTTPException
from app.models import Budget, Category, User
from app.schemas.budget import BudgetCreate, BudgetUpdate


class BudgetRepository:
    @staticmethod
    def create_budget(session: Session, budget_data: BudgetCreate) -> Budget:
        user = session.get(User, budget_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        category = session.get(Category, budget_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        new_budget = Budget.model_validate(budget_data)
        session.add(new_budget)
        session.commit()
        session.refresh(new_budget)
        return new_budget

    @staticmethod
    def get_budgets(session: Session):
        budgets = session.exec(select(Budget)).all()
        return budgets

    @staticmethod
    def get_budget_by_id(session: Session, budget_id: int) -> Budget | None:
        budget = session.get(Budget, budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget

    @staticmethod
    def update_budget(session: Session, budget_id: int, budget_data: BudgetUpdate) -> Budget:
        budget = session.get(Budget, budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        for key, value in budget_data.model_dump(exclude_unset=True).items():
            setattr(budget, key, value)

        session.add(budget)
        session.commit()
        session.refresh(budget)
        return budget

    @staticmethod
    def delete_budget(session: Session, budget_id: int) -> bool:
        budget = session.get(Budget, budget_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")

        session.delete(budget)
        session.commit()
        return True
