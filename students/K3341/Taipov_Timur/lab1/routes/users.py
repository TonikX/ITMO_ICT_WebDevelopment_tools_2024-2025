from datetime import timedelta

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import IntegrityError

from auth import hash_password, verify_passwd, create_access_token, get_current_user
from models import *
from sqlmodel import select

from connection import get_session

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserRead])
def users_list(session=Depends(get_session)):
    """
    Получить список всех пользователей.

    Args:
        session (Session): Сессия базы данных.

    Returns:
        List[UserRead]: Список пользователей.
    """
    return session.exec(select(User)).all()


@router.post("/register")
def register(user: UserCreate, session=Depends(get_session)):
    """
    Зарегистрировать нового пользователя.

    Args:
        user (UserCreate): Данные нового пользователя.
        session (Session): Сессия базы данных.

    Returns:
        dict: Статус и данные созданного пользователя.

    Raises:
        HTTPException: Если пользователь с таким именем уже существует.
    """
    try:
        new_data = {"password": hash_password(user.password)}
        user = User.model_validate(user, update=new_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"status": 200, "data": user}
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="User with this name already exists"
        )


@router.patch("/update")
def reset_password(user: UserUpdate, authorised_user: User = Depends(get_current_user), session=Depends(get_session)):
    """
    Сбросить или изменить пароль авторизованного пользователя.

    Args:
        user (UserUpdate): Новые данные пользователя (обновления).
        authorised_user (User): Текущий авторизованный пользователь.
        session (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    user_data = user.model_dump(exclude_unset=True)
    password = user_data["password"]
    hashed_password = hash_password(password)
    user_data.update({"password": hashed_password})
    authorised_user.sqlmodel_update(user_data)
    session.add(authorised_user)
    session.commit()
    session.refresh(authorised_user)
    return {"status": 200}


@router.post("/login")
def login(user: UserLogin, session=Depends(get_session)):
    """
    Авторизация пользователя и получение JWT токена.

    Args:
        user (UserLogin): Имя пользователя и пароль.
        session (Session): Сессия базы данных.

    Returns:
        dict: JWT токен доступа и тип токена.

    Raises:
        HTTPException: Если имя пользователя или пароль неверны.
    """
    username = user.name
    hashed_password = session.exec(select(User.password).where(User.name == username)).first()
    result = verify_passwd(user.password, hashed_password)
    if not result:
        raise HTTPException(status_code=401, detail="Incorrect password or username")
    payload = {"sub": user.name, "exp": datetime.utcnow() + timedelta(minutes=10)}
    token = create_access_token(payload=payload)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    """
    Получить данные текущего авторизованного пользователя.

    Args:
        current_user (User): Авторизованный пользователь.

    Returns:
        UserRead: Данные пользователя.
    """
    return current_user


@router.delete("/me")
def delete_current_user(session=Depends(get_session), user: User = Depends(get_current_user)):
    """
    Удалить аккаунт текущего авторизованного пользователя.

    Args:
        session (Session): Сессия базы данных.
        user (User): Авторизованный пользователь.

    Returns:
        dict: Подтверждение успешного удаления.
    """
    session.delete(user)
    session.commit()
    return {"ok": True}

