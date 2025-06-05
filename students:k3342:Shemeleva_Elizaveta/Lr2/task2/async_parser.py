import asyncio
import random
from datetime import datetime, timedelta
import time
import aiohttp
from bs4 import BeautifulSoup
import sys
sys.path.append("/Users/shlmlv/PycharmProjects/time-manager")
from sqlmodel import Session
from database import engine
from models import Task, PriorityEnum

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, ssl=False) as resp:
        return await resp.text()

async def parse_itmo(session: aiohttp.ClientSession, url: str):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for card in soup.select("section.announcement__wrapper"):
        title_tag = card.select_one("h4.announcement__wrapper-heading")
        date_tag  = card.select_one("p.announcement__wrapper-date")
        if not title_tag or not date_tag:
            continue
        title = title_tag.text.strip()
        raw_date = date_tag.text.strip().split("—")[0].strip()
        try:
            parts = raw_date.split()
            if len(parts) == 3:
                day, month_name, year = parts
            else:
                day, month_name = parts
                year = str(datetime.now().year)
            month = {
                "января":1, "февраля":2, "марта":3, "апреля":4,
                "мая":5, "июня":6, "июля":7, "августа":8,
                "сентября":9, "октября":10, "ноября":11, "декабря":12
            }[month_name.lower()]
            date_obj = datetime(int(year), month, int(day))
        except:
            date_obj = datetime.now() + timedelta(days=random.randint(1,30))
        priority = random.choice(list(PriorityEnum))
        events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events

async def parse_spbpu(session: aiohttp.ClientSession, url: str):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for card in soup.select("div.event-box.clearfix"):
        title_tag = card.select_one("a.event-header")
        date_tag  = card.select_one("span.e-edge-start")
        if not title_tag or not date_tag:
            continue
        title = title_tag.text.strip()
        raw_date = date_tag.text.strip()
        try:
            day, month_name, year = raw_date.split()
            month = {
                "января":1,"февраля":2,"марта":3,"апреля":4,
                "мая":5,"июня":6,"июля":7,"августа":8,
                "сентября":9,"октября":10,"ноября":11,"декабря":12
            }[month_name.lower()]
            date_obj = datetime(int(year), month, int(day))
        except:
            date_obj = datetime.now() + timedelta(days=random.randint(1,30))
        priority = random.choice(list(PriorityEnum))
        events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events

async def parse_expoforum(session: aiohttp.ClientSession, url: str):
    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, ssl=False) as resp:
        raw = await resp.read()
    html = raw.decode('cp1251', errors='ignore')
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for wrap in soup.select("div.event-slider-wrap"):
        for card in wrap.select("div.event-slider-item"):
            title_tag = card.select_one("div.title-v2")
            date_tag  = card.select_one("div.date")
            if not title_tag or not date_tag:
                continue
            title = title_tag.text.strip()
            raw_date = date_tag.text.strip().split("-")[0].strip()
            try:
                day, month_name = raw_date.split()[:2]
                month = {
                    "января":1,"февраля":2,"марта":3,"апреля":4,
                    "мая":5,"июня":6,"июля":7,"августа":8,
                    "сентября":9,"октября":10,"ноября":11,"декабря":12
                }[month_name.lower()]
                date_obj = datetime(datetime.now().year, month, int(day))
            except:
                date_obj = datetime.now() + timedelta(days=random.randint(1,30))
            priority = random.choice(list(PriorityEnum))
            events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events

async def parse_and_save(url: str, parser):
    async with aiohttp.ClientSession(headers=HEADERS, connector=aiohttp.TCPConnector(ssl=False)) as session:
        events = await parser(session, url)
        with Session(engine) as db:
            db.add_all(events)
            db.commit()
        return len(events)

async def main():
    urls_parsers = [
        ("https://student.itmo.ru/ru/events/", parse_itmo),
        ("https://www.spbstu.ru/media/announcements/", parse_spbpu),
        ("https://www.expoforum.ru/calendar/", parse_expoforum),
    ]
    start_time = time.perf_counter()

    tasks = [parse_and_save(u, p) for u, p in urls_parsers]
    results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - start_time
    total = sum(results)
    print(f"[asyncio] Сохранено {total} событий за {elapsed:.2f} сек")

    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    with open("parser_timings.csv", "a", encoding="utf-8") as log:
        log.write(f"{now},asyncio,{elapsed:.3f}\n")

if __name__ == "__main__":
    start = datetime.now()
    asyncio.run(main())
    print(f"Время выполнения: {(datetime.now()-start).total_seconds()} сек")
