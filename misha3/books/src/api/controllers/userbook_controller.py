from typing import List
from sqlmodel import Session, select
from fastapi import HTTPException

from src.models import UserBook
from pg.schemas.schema import UserBookCreate, UserBookRead


def create_user_book(session: Session, ub_in: UserBookCreate) -> UserBookRead:
    ub = UserBook(**ub_in.dict())
    session.add(ub)
    session.commit()
    session.refresh(ub)
    return UserBookRead.from_orm(ub)


def get_user_books(session: Session) -> List[UserBookRead]:
    user_books = session.exec(select(UserBook)).all()
    return [UserBookRead.from_orm(ub) for ub in user_books]


def get_user_book(session: Session, ub_id: int) -> UserBookRead:
    ub = session.get(UserBook, ub_id)
    if not ub:
        raise HTTPException(status_code=404, detail="UserBook not found")
    return UserBookRead.from_orm(ub)


def update_user_book(session: Session, ub_id: int, ub_in: UserBookCreate) -> UserBookRead:
    ub = session.get(UserBook, ub_id)
    if not ub:
        raise HTTPException(status_code=404, detail="UserBook not found")
    for key, value in ub_in.dict().items():
        setattr(ub, key, value)
    session.add(ub)
    session.commit()
    session.refresh(ub)
    return UserBookRead.from_orm(ub)


def delete_user_book(session: Session, ub_id: int):
    ub = session.get(UserBook, ub_id)
    if not ub:
        raise HTTPException(status_code=404, detail="UserBook not found")
    session.delete(ub)
    session.commit()
    return {"detail": f"UserBook {ub_id} deleted"}
