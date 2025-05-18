from fastapi import HTTPException
from starlette import status

from app.models.models import User
from app.schemas.user import UserCreate, ChangePassword, UserUpdate
from app.core.security import AuthHandler
from typing import Optional
from sqlmodel import select, Session

auth_handler = AuthHandler()

def create_user(user_create: UserCreate, session: Session) -> User:
    """
    Создаёт нового пользователя:
    - Проверяет, существует ли уже пользователь.
    - Хэширует пароль.
    - Сохраняет пользователя в БД.
    """
    statement = select(User).where(
        (User.username == user_create.username) | (User.email == user_create.email)
    )
    existing_user: Optional[User] = session.exec(statement).first()
    if existing_user:
        raise ValueError("Username or email already exists")

    user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=auth_handler.get_password_hash(user_create.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def authenticate_user(username: str, password: str, session: Session) -> Optional[str]:
    """
    Проверяет пользователя по username и паролю.
    Если данные верные, возвращает JWT-токен.
    """
    statement = select(User).where(User.username == username)
    user: Optional[User] = session.exec(statement).first()
    if not user:
        return None
    if not auth_handler.verify_password(password, user.hashed_password):
        return None
    return auth_handler.encode_token(str(user.id))

def get_user_by_id(user_id: int, session: Session) -> User | None:
    """
    Ищет пользователя по ID.
    Если не найден — вызывает HTTP 404.
    """
    return session.get(User, user_id)

def get_all_users(session: Session, username: str | None = None) -> list[User]:
    """
    Возвращает всех пользователей (опционально фильтрует по username).
    """
    statement = select(User)
    if username:
        statement = statement.where(User.username.ilike(f"{username}%"))
    return session.exec(statement).all()

def change_user_password(user_id: int, password_data: ChangePassword, session: Session):
    """
    Меняет пароль пользователя.
    - Проверяет старый пароль.
    - Устанавливает новый хэшированный пароль.
    """
    user = session.get(User, user_id)
    if not auth_handler.verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    if password_data.old_password == password_data.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password must be different")

    user.hashed_password = auth_handler.get_password_hash(password_data.new_password)
    session.commit()
    session.refresh(user)

def update_user(user_id: int, user_update: UserUpdate, session: Session) -> User:
    """
    Обновляет профиль пользователя (username, age, info).
    """
    user = session.get(User, user_id)

    if user_update.username and user_update.username != user.username:
        existing_user = session.exec(select(User).where(User.username == user_update.username)).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user.username = user_update.username

    if user_update.age is not None:
        user.age = user_update.age
    if user_update.info is not None:
        user.info = user_update.info

    session.commit()
    session.refresh(user)

    return user

