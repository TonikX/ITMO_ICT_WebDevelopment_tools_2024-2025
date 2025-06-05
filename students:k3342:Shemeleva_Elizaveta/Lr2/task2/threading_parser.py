import threading
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
from sqlmodel import Session
import time
import sys
import os
sys.path.append("/Users/shlmlv/PycharmProjects/time-manager")
from models import Task, PriorityEnum
from database import engine, init_db


def fix_encoding(raw: str) -> str:
    try:
        return raw.encode("latin1").decode("utf-8")
    except UnicodeError:
        return raw


def parse_event_itmo(url):
    events = []
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    for card in soup.select("section.announcement__wrapper"):
        title_tag = card.select_one("h4.announcement__wrapper-heading")
        date_tag = card.select_one("p.announcement__wrapper-date")
        if not title_tag or not date_tag:
            continue
        raw_title = title_tag.text.strip()
        title = fix_encoding(raw_title)
        raw_date_full = date_tag.text.strip()
        raw_date = raw_date_full.split("-")[0].strip()
        date_str = fix_encoding(raw_date)
        try:
            day, month = date_str.split()
            month_map = {
                "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
                "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
            }
            date_obj = datetime(datetime.now().year, month_map[month.lower()], int(day))
        except:
            date_obj = datetime.now() + timedelta(days=random.randint(1, 30))
        priority = random.choice(list(PriorityEnum))
        events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events


def parse_event_spbpu(url):
    events = []
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    for card in soup.select("div.event-box.clearfix"):
        title_tag = card.select_one("a.event-header")
        date_tag = card.select_one("span.e-edge-start")
        if not title_tag or not date_tag:
            continue
        raw_title = title_tag.text.strip()
        title = fix_encoding(raw_title)
        title = raw_title
        raw_date = date_tag.text.strip()
        date_str = fix_encoding(raw_date)
        try:
            day, month_name, year = date_str.split()
            month_map = {
                "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
                "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
            }
            date_obj = datetime(int(year), month_map[month_name.lower()], int(day))
        except:
            date_obj = datetime.now() + timedelta(days=random.randint(1, 30))
        priority = random.choice(list(PriorityEnum))
        events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events


def parse_event_expoforum(url):
    events = []
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    # проходим по всем блокам event-slider-wrap
    for wrap in soup.select("div.event-slider-wrap"):
        for card in wrap.select("div.event-slider-item"):
            title_tag = card.select_one("div.title-v2")
            date_tag = card.select_one("div.date")
            if not title_tag or not date_tag:
                continue
            raw_title = title_tag.text.strip()
            title = fix_encoding(raw_title)
            raw_date = date_tag.text.strip()
            date_str = fix_encoding(raw_date)
            try:
                parts = date_str.split("-")
                if len(parts) == 2:
                    start_date_str = parts[0].strip()
                else:
                    start_date_str = date_str.strip()
                day, month_name = start_date_str.split()[:2]
                month_map = {
                    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
                    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
                }
                year = 2025
                date_obj = datetime(year, month_map[month_name.lower()], int(day))
            except:
                date_obj = datetime.now() + timedelta(days=random.randint(1, 30))
            priority = random.choice(list(PriorityEnum))
            events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events


def parse_and_save(url, all_events):
    print(f"Парсим {url}")
    if "itmo.ru" in url:
        events = parse_event_itmo(url)
    elif "spbstu.ru" in url:
        events = parse_event_spbpu(url)
    elif "expoforum.ru" in url:
        events = parse_event_expoforum(url)
    else:
        print(f"[!] Для {url} парсер не реализован")
        events = []
    all_events.extend(events)

def main():
    from database import init_db
    init_db()

    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    threads = []
    all_events = []

    start_time = time.perf_counter()

    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url, all_events))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    with Session(engine) as session:
        session.add_all(all_events)
        session.commit()

    elapsed = time.perf_counter() - start_time
    print(f"[threading] Найдено/сохранено {len(all_events)} событий за {elapsed:.2f} сек")

    with open("parser_timings.csv", "a", encoding="utf-8") as log:
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        log.write(f"{now},threading,{elapsed:.3f}\n")

if __name__ == "__main__":
    main()
