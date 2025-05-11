import re
from sqlmodel import Session, select
from schemas.error import Error
from db.models import User


def validate_username(username, errors: Error, session: Session):
    """
    Проверяет username:
      - длина не менее 5 символов;
      - содержит только латинские буквы, цифры, точку и нижнее подчёркивание;
      - не содержит спецсимволы в начале/конце и не содержит подряд несколько спецсимволов;
      - username уникален.
    """
    if len(username) < 5:
        errors.add_error("username", "Username must be at least 5 characters long.")

    username_regex = r"^(?![._])(?!.*[._]{2})[A-Za-z0-9._]+(?<![._])$"
    if not re.match(username_regex, username):
        errors.add_error("username", "Username contains invalid characters or improper special symbol placement.")

    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        errors.add_error("username", "Username already exists.")


def validate_email(email, errors: Error, session: Session):
    """
    Проверяет email:
      - маску адреса электронной почты;
      - email уникален.
    """
    email_regex = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
    if not re.match(email_regex, email):
        errors.add_error("email", "Email address is invalid.")

    existing_email = session.exec(select(User).where(User.email == email)).first()
    if existing_email:
        errors.add_error("email", "Email already registered.")


def validate_password(password, errors: Error):
    """
    Проверяет пароль:
      - длина не менее 8 символов;
      - содержит хотя бы одну заглавную букву;
      - содержит хотя бы одну строчную букву;
      - содержит хотя бы одну цифру.
    """
    if len(password) < 8:
        errors.add_error("password", "Password must be at least 8 characters long.")
    if not re.search(r'[A-ZА-Я]', password):
        errors.add_error("password", "Password must contain at least one uppercase letter.")
    if not re.search(r'[a-zа-я]', password):
        errors.add_error("password", "Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
        errors.add_error("password", "Password must contain at least one digit.")


def validate_age(age: int, errors: Error):
    if age < 18:
        errors.add_error("age", "Age cannot be less than 18.")


def validate_registration(user_data, errors: Error, session: Session):
    validate_username(user_data.username.strip(), errors, session)
    validate_email(user_data.email.strip(), errors, session)
    validate_password(user_data.password, errors)
    if user_data.age is not None:
        validate_age(user_data.age, errors)
