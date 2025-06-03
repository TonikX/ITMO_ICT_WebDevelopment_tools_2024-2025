import os
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
pepper = os.getenv('PEPPER')

pwd_context = CryptContext(schemes=["argon2"])

def hash_password(plain_password: str) -> str:
    pwd_with_pepper = plain_password + pepper
    return pwd_context.hash(pwd_with_pepper)

def verify_password(plain_password: str, hashed: str) -> bool:
    pwd_with_pepper = plain_password + pepper
    return pwd_context.verify(pwd_with_pepper, hashed)
