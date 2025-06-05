import asyncio
import random
from datetime import datetime, timedelta

import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import SQLModel

from .database import engine_async, AsyncSessionLocal
from .models import Task, PriorityEnum


async def init_db():
    async with engine_async.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, ssl=False) as resp:
        return await resp.text()


async def parse_itmo(session: aiohttp.ClientSession, url: str):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for card in soup.select("section.announcement__wrapper"):
        title_tag = card.select_one("h4.announcement__wrapper-heading")
        date_tag = card.select_one("p.announcement__wrapper-date")
        if not title_tag or not date_tag:
            continue

        title = title_tag.text.strip()
        raw_date_full = date_tag.text.strip()
        raw_date = raw_date_full.split("-")[0].strip()

        try:
            day, month = raw_date.split()
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


async def parse_spbpu(session: aiohttp.ClientSession, url: str):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for card in soup.select("div.event-box.clearfix"):
        t = card.select_one("a.event-header")
        d = card.select_one("span.e-edge-start")
        if not t or not d:
            continue
        title = t.text.strip()
        raw_date = d.text.strip()
        try:
            day, month_name, year = raw_date.split()
            m = {
                "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
                "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
            }[month_name.lower()]
            date_obj = datetime(int(year), m, int(day))
        except:
            date_obj = datetime.now() + timedelta(days=random.randint(1, 30))
        priority = random.choice(list(PriorityEnum))
        events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events


async def parse_expoforum(session: aiohttp.ClientSession, url: str):
    html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    events = []
    for wrap in soup.select("div.event-slider-wrap"):
        for card in wrap.select("div.event-slider-item"):
            t = card.select_one("div.title-v2")
            d = card.select_one("div.date")
            if not t or not d:
                continue
            title = t.text.strip()
            ds = d.text.strip().split("-")[0].strip()
            try:
                day, month_name = ds.split()[:2]
                m = {
                    "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
                    "мая": 5, "июня": 6, "июля": 7, "августа": 8,
                    "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
                }[month_name.lower()]
                date_obj = datetime(2025, m, int(day))
            except:
                date_obj = datetime.now() + timedelta(days=random.randint(1, 30))
            priority = random.choice(list(PriorityEnum))
            events.append(Task(description=title, due_date=date_obj, priority=priority))
    return events


async def parse_and_save(url: str, parser):
    async with aiohttp.ClientSession() as http_sess:
        events = await parser(http_sess, url)

    if not events:
        print(f"Сохранено 0 событий из {url}")
        return

    async with AsyncSessionLocal() as db:
        async with db.begin():
            db.add_all(events)

    print(f"Сохранено {len(events)} событий из {url}")


async def main():
    await init_db()

    urls_parsers = [
        ("https://student.itmo.ru/ru/events/", parse_itmo),
        ("https://www.spbstu.ru/media/announcements/", parse_spbpu),
        ("https://www.expoforum.ru/calendar/", parse_expoforum),
    ]
    tasks = [parse_and_save(u, p) for u, p in urls_parsers]
    start = datetime.now()
    await asyncio.gather(*tasks)
    print("Время выполнения:", (datetime.now() - start).total_seconds(), "сек")


if __name__ == "__main__":
    asyncio.run(main())
