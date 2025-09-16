from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from models.tables import User, Category, Transaction, Budget, Goal, Notification
from services.hashing import get_password_hash

def create_entity(session: Session, model, data: dict):
    db_entity = model(**data)
    session.add(db_entity)
    session.commit()
    session.refresh(db_entity)
    return db_entity

def get_entity(session: Session, model, entity_id: int, user_id: int = None):
    entity = session.get(model, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    if hasattr(entity, "user_id") and user_id and entity.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return entity

def get_entities(session: Session, model, user_id: int = None):
    if user_id and hasattr(model, "user_id"):
        return session.exec(select(model).where(model.user_id == user_id)).all()
    return session.exec(select(model)).all()

def delete_entity(session: Session, model, entity_id: int, user_id: int = None):
    entity = session.get(model, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    if hasattr(entity, "user_id") and user_id and entity.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    session.delete(entity)
    session.commit()

def get_user_by_credential(session: Session, credential: str):
    return session.exec(select(User).where((User.username == credential) | (User.email == credential))).first()

def create_user(session: Session, user_create):
    existing_user = get_user_by_credential(session, user_create.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_user = get_user_by_credential(session, user_create.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user_with_relations(session: Session, user_id: int):
    return session.exec(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.categories),
            selectinload(User.transactions),
            selectinload(User.budgets),
            selectinload(User.goals),
            selectinload(User.notifications)
        )
    ).first()

def get_category_with_transactions(session: Session, category_id: int, user_id: int):
    return session.exec(
        select(Category)
        .where(Category.id == category_id, Category.user_id == user_id)
        .options(selectinload(Category.transactions))
    ).first()
    
def get_categories_with_transactions(session: Session, user_id: int) -> list[Category]:
    statement = (
        select(Category)
        .where(Category.user_id == user_id)
        .options(selectinload(Category.transactions))
    )
    result = session.exec(statement)
    return result.all()