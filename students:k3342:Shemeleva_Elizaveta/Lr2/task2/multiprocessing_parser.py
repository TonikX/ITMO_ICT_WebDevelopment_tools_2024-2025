import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import time
from multiprocessing import Pool
from sqlalchemy.orm import Session
import sys
sys.path.append("/Users/shlmlv/PycharmProjects/time-manager")
from database import engine
from models import Task, PriorityEnum
from threading_parser import parse_event_itmo, parse_event_spbpu, parse_event_expoforum

URL_PARSER_MAP = {
    "https://student.itmo.ru/ru/events/": parse_event_itmo,
    "https://www.spbstu.ru/media/announcements/": parse_event_spbpu,
    "https://www.expoforum.ru/calendar/": parse_event_expoforum,
}


def parse_and_save(url: str):
    print(f"Парсим {url}")
    parser_func = URL_PARSER_MAP.get(url)
    if not parser_func:
        print(f"Нет обработчика для {url}")
        return 0

    events = parser_func(url)
    with Session(engine) as session:
        session.add_all(events)
        session.commit()
        print(f"Сохранено {len(events)} событий из {url}")
        return len(events)


def main():
    with open("urls.txt", "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    start_time = time.perf_counter()

    with Pool(processes=len(urls)) as pool:
        results = pool.map(parse_and_save, urls)

    elapsed = time.perf_counter() - start_time
    total = sum(results)
    print(f"[multiprocessing] Сохранено {total} событий за {elapsed:.2f} сек")

    with open("parser_timings.csv", "a", encoding="utf-8") as log:
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        log.write(f"{now},multiprocessing,{elapsed:.3f}\n")


if __name__ == "__main__":
    main()
