import hashlib
import hmac
import base64
import json
import time
from os import environ

from fastapi import Header, HTTPException, status, Depends
from connection import SessionLocal
from models.user_model import User

# Секретный ключ для подписи JWT-токенов
SECRET_KEY = environ.get("SECRET_KEY", "mysecretkey")

def get_password_hash(password: str) -> str:
    """
    Создает хэш для пароля с использованием SHA256 и соли.
    Здесь используется фиксированная соль; в продакшене рекомендуется применять уникальную соль для каждого пользователя.
    """
    salt = "static_salt"  # Можно заменить на более сложный алгоритм генерации соли
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет совпадение предоставленного пароля с хэшированным паролем.
    """
    return get_password_hash(plain_password) == hashed_password

def create_jwt_token(payload: dict) -> str:
    """
    Создает JWT-токен:
    - Формирует заголовок.
    - Добавляет полезную нагрузку с временем истечения (exp).
    - Кодирует заголовок и payload в Base64 с единообразным форматом.
    - Создает подпись с использованием HMAC SHA256.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    # Добавляем время истечения токена (например, 1 час)
    payload["exp"] = int(time.time()) + 3600

    def b64_encode(data: str) -> str:
        # Используем компактное представление: без пробелов между элементами и с сортировкой ключей
        return base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8").rstrip("=")

    header_json = json.dumps(header, separators=(",", ":"), sort_keys=True)
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    header_enc = b64_encode(header_json)
    payload_enc = b64_encode(payload_json)
    signing_input = f"{header_enc}.{payload_enc}"

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        msg=signing_input.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()

    signature_enc = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    jwt_token = f"{signing_input}.{signature_enc}"
    return jwt_token

def verify_jwt_token(token: str) -> bool:
    """
    Проверяет валидность переданного JWT-токена:
    - Пересчитывает подпись и сравнивает с переданной.
    - Проверяет значение exp в полезной нагрузке.
    """
    try:
        header_enc, payload_enc, signature_enc = token.split(".")
        signing_input = f"{header_enc}.{payload_enc}"
        expected_signature = hmac.new(
            SECRET_KEY.encode("utf-8"),
            msg=signing_input.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        expected_signature_enc = base64.urlsafe_b64encode(expected_signature).decode("utf-8").rstrip("=")

        if not hmac.compare_digest(expected_signature_enc, signature_enc):
            return False

        # Добавляем недостающие символы '=' для корректного декодирования Base64
        padding = "=" * (-len(payload_enc) % 4)
        payload_json = base64.urlsafe_b64decode(payload_enc + padding).decode("utf-8")
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < time.time():
            return False

        return True
    except Exception:
        return False

def decode_jwt(token: str) -> dict:
    """
    Декодирует JWT-токен и возвращает полезную нагрузку в виде словаря.
    """
    try:
        _, payload_enc, _ = token.split(".")
        padding = "=" * (-len(payload_enc) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_enc + padding)
        payload = json.loads(payload_bytes.decode("utf-8"))
        return payload
    except Exception:
        return {}

def get_current_user(
    authorization: str = Header(..., include_in_schema=False)
):
    """
    Извлекает токен из заголовка Authorization и возвращает объект пользователя.
    Ожидается, что токен имеет вид "Bearer <token>".
    Использование include_in_schema=False скрывает этот заголовок в документации Swagger UI.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication header"
        )
    token = authorization[len("Bearer "):]

    if not verify_jwt_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    payload = decode_jwt(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Получаем пользователя из БД
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    return user