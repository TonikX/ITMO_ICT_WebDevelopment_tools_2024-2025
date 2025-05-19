import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
from passlib.context import CryptContext
from sqlmodel import Session
from models.finance_models import User
from db.connection import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def parse_and_save(url: str) -> None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        username_tag = soup.select_one("a.tm-user-card__nickname")
        if not username_tag:
            raise ValueError("Username not found")
        base_username = username_tag.text.strip().lstrip("@")
        username = f"{base_username}_multiprocessing"
        email = f"{username}@multiprocessing.ru"

        hashed_password = pwd_context.hash(base_username)

        name_tag = soup.select_one("span.tm-user-card__name")
        if name_tag:
            name_parts = name_tag.text.strip().split()
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        else:
            first_name = base_username
            last_name = "Unknown"

        with Session(engine) as db:
            user = User(
                username=username,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            db.add(user)
            db.commit()

        print(f"Multiprocessing: User added {username} ({first_name} {last_name})")

    except Exception as e:
        print(f"Multiprocessing: Error {url}: {e}")


def main(urls: list[str]) -> None:
    start_time = time.time()
    with multiprocessing.Pool(processes=len(urls)) as pool:
        pool.map(parse_and_save, urls)
    print(f"Time: {time.time() - start_time:.2f} seconds")
