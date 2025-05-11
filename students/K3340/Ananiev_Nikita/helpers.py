from sqlmodel import SQLModel, Session
from fastapi import HTTPException
from typing import Dict


def get_object_by_id(obj_id: int, obj_model_class, session: Session):
    obj = session.get(obj_model_class, obj_id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{obj_model_class.__name__} not found")
    return obj


def upd_model(model: SQLModel, updates: Dict[str, any], session: Session):
    for key, value in updates.items():
        setattr(model, key, value)
    session.add(model)
    session.commit()
    session.refresh(model)
    return model
