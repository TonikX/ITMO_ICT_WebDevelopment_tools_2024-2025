from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from app.models.models import Ownership
from app.api.dependencies.auth import get_current_user
from app.db.session import get_session


def get_current_ownership(
    book_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Проверяет, владеет ли пользователь книгой."""
    statement = select(Ownership).where(
        (Ownership.book_id == book_id) &
        (Ownership.user_id == user_id) &
        (Ownership.is_current == True)
    )
    ownership = session.exec(statement).first()

    if not ownership:
        raise HTTPException(status_code=400, detail="You do not currently own this book")

    return ownership

def is_original_owner(
    book_id: int,
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> bool:
    """Проверяет, является ли пользователь первым владельцем книги."""
    statement = select(Ownership).where(Ownership.book_id == book_id)
    ownerships = session.exec(statement).all()

    return len(ownerships) == 1 and ownerships[0].user_id == user_id
