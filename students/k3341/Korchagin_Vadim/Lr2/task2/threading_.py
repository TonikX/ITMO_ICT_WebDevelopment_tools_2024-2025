import threading
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
        username = f"{base_username}_threading"
        email = f"{username}@threading.ru"
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

        print(f"Threading: User added {username} ({first_name} {last_name})")

    except Exception as e:
        print(f"Threading: Error {url}: {e}")


def main(urls: list[str]) -> None:
    start_time = time.time()
    threads = []

    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"Time: {time.time() - start_time:.2f} seconds")
