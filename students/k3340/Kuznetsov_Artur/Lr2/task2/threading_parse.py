import threading
import time
import requests
from bs4 import BeautifulSoup
from passlib.context import CryptContext
from sqlmodel import Session
from models import Users
from connection import engine

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


def parse_and_save(url):
    try:
        # Загрузка страницы
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Извлечение username
        username_tag = soup.find("a", class_ = "tm-user-card__nickname")
        if not username_tag:
            raise ValueError("No username found")
        base_username = username_tag.text.strip().lstrip('@')
        username = f"{base_username}_threading"

        # Формирование email и password
        email = f"{username}@threading.ru"
        hashed_password = pwd_context.hash(base_username)

        # Извлечение имени и фамилии
        name_tag = soup.find("span", class_ = "tm-user-card__name")
        if not name_tag:
            raise ValueError("No name found")
        full_name = name_tag.text.strip()
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"

        # Сохранение в базу данных
        with Session(engine) as session:
            user = Users(
                username = username,
                password = hashed_password,
                first_name = first_name,
                last_name = last_name,
                email = email
            )
            session.add(user)
            session.commit()
        print(f"Threading: User added {username} ({first_name} {last_name})")
    except Exception as e:
        print(f"Threading: Error {url}: {e}")


def main(urls):
    start_time = time.time()
    threads = []

    for url in urls:
        thread = threading.Thread(target = parse_and_save, args = (url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()

    print(f"Time: {end_time - start_time:.2f} seconds")
