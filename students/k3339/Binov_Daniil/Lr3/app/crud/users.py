from sqlmodel import Session, select
from typing import Optional
from app.models import User
from app.schemas import UserCreate, UserRead
from app.utils.security import get_password_hash

def create_user(session: Session, user: UserCreate) -> User:
    existing_user = get_user_by_username(session, username=user.username)
    if existing_user:
        raise ValueError("Username already exists")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user(session: Session, user_id: int) -> Optional[User]:
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def update_user_password(session: Session, user: User, new_password: str) -> User:
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_users(session: Session) -> list[User]:
    statement = select(User)
    return session.exec(statement).all()