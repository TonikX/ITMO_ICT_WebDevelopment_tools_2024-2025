from multiprocessing import Process
import requests
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
import time
from models import Tag

# Настройка базы данных
DATABASE_URL = "postgresql://christina:123@localhost:5433/timemngmt_db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# Список URL-ов
urls = [
    "https://quotes.toscrape.com/page/1/",
    "https://quotes.toscrape.com/page/2/",
    "https://quotes.toscrape.com/page/3/",
]

# Функция парсинга и сохранения тегов
def parse_and_save(url: str):
    try:
        print(f"[Process] Парсим: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        tag_elements = soup.select("a.tag")

        with Session(engine) as session:
            for tag_el in tag_elements:
                tag_name = tag_el.text.strip()
                if tag_name:
                    exists = session.exec(select(Tag).where(Tag.name == tag_name)).first()
                    if not exists:
                        session.add(Tag(name=tag_name))
                        print(f"[Process] Сохранили тег: {tag_name}")
            session.commit()
    except Exception as e:
        print(f"[Process] Ошибка при обработке {url}: {e}")

# Точка входа
if __name__ == "__main__":
    processes = []
    start_time = time.time()

    for url in urls:
        p = Process(target=parse_and_save, args=(url,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    end_time = time.time()
    print(f"\n Готово! Обработано {len(urls)} страниц за {round(end_time - start_time, 2)} сек.")
