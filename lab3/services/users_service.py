from sqlmodel import Session, select
from auth.utils import get_password_hash, verify_password, create_access_token
from models.models import Account


def get_all_users(session: Session) -> list[dict]:
    statement = select(Account)
    results = session.exec(statement).all()
    users = [user.model_dump(exclude={"password"}) for user in results]
    return users


def get_user_by_id(session: Session, user_id: int) -> Account | None:
    statement = select(Account).where(Account.id == user_id)
    result = session.exec(statement).first()
    if not result:
        return None
    return result


def create_user(session: Session, user: Account) -> Account:
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user_id: int, user: Account) -> Account | None:
    existing_user = get_user_by_id(session, user_id)
    if not existing_user:
        return None
    for key, value in user.model_dump(exclude_unset=True).items():
        setattr(existing_user, key, value)
    session.commit()
    session.refresh(existing_user)
    return existing_user


def delete_user(session: Session, user_id: int) -> bool:
    existing_user = get_user_by_id(session, user_id)
    if not existing_user:
        return False
    session.delete(existing_user)
    session.commit()
    return True


def login_user(session: Session, username: str, password: str) -> str | None:
    statement = select(Account).where(Account.username == username)
    user = session.exec(statement).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    token = create_access_token(role=user.role, user_id=user.id)
    return token


def register_user(session: Session, user: Account) -> Account:
    existing_user = get_user_by_id(session, user.id)
    if existing_user:
        return None
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def change_password(session: Session, user_id: int, old_password: str, new_password: str) -> bool:
    user = get_user_by_id(session, user_id)
    if not user:
        return False

    if not verify_password(old_password, user.password):
        return False

    user.password = get_password_hash(new_password)
    session.commit()
    return True
