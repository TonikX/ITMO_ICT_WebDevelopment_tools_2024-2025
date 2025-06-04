from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.tables import User, Category, Transaction, Budget, Goal, Notification, TransactionCategoryLink

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