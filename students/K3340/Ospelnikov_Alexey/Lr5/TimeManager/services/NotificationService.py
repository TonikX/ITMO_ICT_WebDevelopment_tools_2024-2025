from typing import Optional, List
from datetime import datetime
from models.notification import *
from fastapi import FastAPI, Depends, APIRouter, HTTPException
from sqlmodel import SQLModel, Field, Relationship, Column, TIMESTAMP, text

def new_notification_create(notification: Notification, session) -> Notification:
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return {"status": 200, "data": notification}


def list_all_notifications(session) -> List[Notification]:
    return session.exec(select(Notification)).all()


def get_notification_by_id(notification_id: int, session) -> Notification:
    data = session.exec(select(Notification).where(Notification.id == notification_id)).first()
    if not data:
        raise HTTPException(status_code=404, detail="Notification not found")    
    return data

def delete_notification(notification_id: int, session):
    notification = session.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    session.delete(notification)
    session.commit()
    return {"ok": True}    

def patch_notification(notification_id: int, notification: Notification, session) -> Notification:
    db_notification = session.get(Notification, notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification_data = notification.model_dump(exclude_unset=True)
    for key, value in notification_data.items():
        setattr(db_notification, key, value)
    session.add(db_notification)
    session.commit()
    session.refresh(db_notification)
    return db_notification