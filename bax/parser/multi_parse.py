from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session

from connection import engine
from models import Page


def parse_and_save(url):
    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
        html = result.text
        bs = BeautifulSoup(html, "html.parser")
        title = bs.title.string if bs.title else bs.find("h1").text.strip() if bs.find("h1") else None
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return

    with Session(engine) as db:
        page = Page(url=url, title=title)
        db.add(page)
        db.commit()
        print(f"Парсинг завершён: {url} | Заголовок: {title}")


def multi_parse(urls, num_processes=4):
    with Pool(num_processes) as pool:
        pool.map(parse_and_save, urls)

