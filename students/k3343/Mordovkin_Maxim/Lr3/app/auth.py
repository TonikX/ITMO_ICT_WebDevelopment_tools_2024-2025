import os
import time
import json
import hmac
import hashlib
from typing import Optional
import base64
import secrets
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SECRET = "66666666666666666666666"
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 3600

def _urlsafe_base64_encode(data: bytes) -> str:

    raw = base64.urlsafe_b64encode(data).decode("utf-8")
    return raw.rstrip('=')

class PasswordHasher:
    """
    Класс для хэширования паролей с уникальными солями
    """
    @staticmethod
    def generate_salt() -> str:
        return secrets.token_hex(8)  # 16-символьная соль

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """Хэшируем пароль + соль через SHA256."""
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    @staticmethod
    def verify_password(password: str, salt: str, expected_hash: str) -> bool:
        return PasswordHasher.hash_password(password, salt) == expected_hash

class TokenService:
    """
    Класс для генерации и проверки jwt токенов.
    """
    def __init__(self, secret: str = SECRET_KEY, algorithm: str = JWT_ALGORITHM):
        self.secret = secret
        self.algorithm = algorithm

    def create_jwt(self, payload: dict) -> str:
        header = {"alg": self.algorithm, "typ": "JWT"}
        # кодирование header
        header_b64 = _urlsafe_base64_encode(json.dumps(header).encode("utf-8"))

        # добавление времени истечения
        payload_copy = dict(payload)
        payload_copy["exp"] = int(time.time()) + JWT_EXPIRATION_SECONDS
        payload_b64 = _urlsafe_base64_encode(json.dumps(payload_copy).encode("utf-8"))

        # подписываем
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        signature_bytes = hmac.new(
            self.secret.encode("utf-8"),
            signing_input,
            hashlib.sha256
        ).digest()
        signature_b64 = _urlsafe_base64_encode(signature_bytes)
        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def verify_jwt(self, token: str) -> Optional[dict]:
        try:
            header_b64, payload_b64, signature_b64 = token.split('.')
            signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

            expected_signature = hmac.new(
                self.secret.encode("utf-8"),
                signing_input,
                hashlib.sha256
            ).digest()
            expected_b64 = _urlsafe_base64_encode(expected_signature)
            if not hmac.compare_digest(expected_b64, signature_b64):
                return None

            # декодирование payload
            padded_b64 = payload_b64 + '=' * (-len(payload_b64) % 4)
            payload_data = base64.urlsafe_b64decode(padded_b64.encode("utf-8"))
            payload_json = json.loads(payload_data.decode("utf-8"))

            # проверка срока действия
            if payload_json.get("exp", 0) < time.time():
                return None

            return payload_json
        except Exception:
            return None


hasher = PasswordHasher()
token_service = TokenService()

def hash_password(password: str) -> str:
    """
    Генерирует соль, хэш + соль в одну строку
    """
    salt = hasher.generate_salt()
    pass_hash = hasher.hash_password(password, salt)
    return f"{salt}${pass_hash}"

def verify_password(password: str, stored_value: str) -> bool:
    """
    Извлекает соль и сравнивает хэш
    """
    try:
        salt, actual_hash = stored_value.split('$', 1)
    except ValueError:
        return False
    return hasher.verify_password(password, salt, actual_hash)

def create_jwt(payload: dict) -> str:
    return token_service.create_jwt(payload)

def verify_jwt(token: str) -> Optional[dict]:
    return token_service.verify_jwt(token)
