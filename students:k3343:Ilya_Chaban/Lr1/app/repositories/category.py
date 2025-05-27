from sqlmodel import Session, select
from app.models import Category, Goal
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    @staticmethod
    def create_category(session: Session, category_data: CategoryCreate) -> Category:
        category = Category.model_validate(category_data)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def get_categories(session: Session):
        categories = session.exec(select(Category)).all()
        return categories

    @staticmethod
    def get_category_by_id(session: Session, category_id: int) -> Category | None:
        category = session.get(Category, category_id)
        return category

    @staticmethod
    def update_category(session: Session, category_id: int, category_data: CategoryUpdate) -> Category | None:
        category = session.get(Category, category_id)
        if not category:
            return None
        for key, value in category_data.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def delete_category(session: Session, category_id: int) -> bool:
        category = session.get(Category, category_id)
        if not category:
            return False
        session.delete(category)
        session.commit()
        return True

    @staticmethod
    def get_categories_for_user(session, user_id: int):
        statement = (
            select(Category)
            .join(GoalCategoryLink, GoalCategoryLink.category_id == Category.id)
            .join(Goal, Goal.id == GoalCategoryLink.goal_id)
            .where(Goal.user_id == user_id)
        )
        result = session.exec(statement)
        return result.all()
