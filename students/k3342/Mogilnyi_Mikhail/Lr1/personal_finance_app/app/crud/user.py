from sqlmodel import Session, select
from app.models.user import User

def get_user_by_username(session: Session, username: str) -> User:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def get_user(session: Session, user_id: int) -> User:
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()

def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
