from sqlmodel import select
from app.connection import get_session
from app.models import User


def select_all_users():
    with next(get_session()) as session:
        statement = select(User)
        res = session.exec(statement).all()
        return res


def find_user(email):
    if not isinstance(email, str):
        raise ValueError(f"Expected a string for email, but got {type(email)}")
    print(f"Searching for user with email: {email}")
    with next(get_session()) as session:
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()


def create_user(user_data):
    with next(get_session()) as session:
        user = User.model_validate(user_data)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def update_user(user_id, user_data: dict):
    with next(get_session()) as session:
        user = session.get(User, user_id)
        print(f"Before update: {user.password}")
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"After update: {user.password}")
    return user

