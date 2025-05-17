import os
from datetime import timedelta
from typing import Optional, Annotated
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

import fastapi
from passlib.hash import argon2
from sqlmodel import Session, select

from connection import get_session
from models import User

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(password: str) -> str:
    """
    Захешировать пароль с использованием алгоритма Argon2.

    Args:
        password (str): Обычный пароль в виде строки.

    Returns:
        str: Хешированный пароль.
    """
    hashed = argon2.hash(password)
    return hashed


def verify_passwd(password: str, hashed_password: str) -> bool:
    """
    Проверить соответствие пароля и его хеша.

    Args:
        password (str): Введённый пользователем пароль.
        hashed_password (str): Хешированный пароль.

    Returns:
        bool: True, если пароль верный, иначе False.
    """
    result = argon2.verify(password, hashed_password)
    return result


def create_access_token(payload: dict) -> str:
    """
    Создать JWT токен на основе переданного payload.

    Args:
        payload (dict): Данные, которые будут зашифрованы в токене.

    Returns:
        str: Сгенерированный JWT токен.
    """
    secret_key = os.getenv("SECRET_KEY")
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def verify_token(token: str) -> str:
    """
    Проверить JWT токен и извлечь имя пользователя.

    Args:
        token (str): JWT токен.

    Returns:
        str: Имя пользователя (sub), если токен валиден.

    Raises:
        HTTPException: Если токен недействителен или не содержит имя пользователя.
    """
    secret_key = os.getenv("SECRET_KEY")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        name = payload.get("sub")
        return name
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session=Depends(get_session)) -> User:
    """
    Получить текущего авторизованного пользователя по токену.

    Args:
        token (str): JWT токен, переданный пользователем.
        session (Session): Сессия базы данных.

    Returns:
        User: Объект пользователя.

    Raises:
        HTTPException: Если токен недействителен или пользователь не найден.
    """
    name = verify_token(token)
    user = session.exec(select(User).where(User.name == name)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



