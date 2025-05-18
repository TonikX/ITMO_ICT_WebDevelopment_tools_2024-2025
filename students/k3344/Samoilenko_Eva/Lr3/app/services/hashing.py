import hashlib
import os


# Функция для хэширования пароля с солью
def hash_password(password: str) -> str:
    salt = os.urandom(16)  # Генерируем случайную соль
    password_salt = password.encode('utf-8') + salt  # Сочетаем пароль и соль
    hashed_password = hashlib.sha256(password_salt).hexdigest()  # Хэшируем результат
    return hashed_password, salt


# Проверка пароля
def verify_password(plain_password: str, hashed_password: str, salt: bytes) -> bool:
    password_salt = plain_password.encode('utf-8') + salt  # Сочетаем введённый пароль с солью
    return hashlib.sha256(password_salt).hexdigest() == hashed_password
