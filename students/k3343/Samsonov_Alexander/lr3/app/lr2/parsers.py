from multiprocessing import Process
from threading import Thread

import httpx
from sqlmodel import Session

from app.db.session import sync_engine
from app.models import Story, Comment
from app.task_manager.utils import convert_unix_time

API_BASE_URL = "https://hacker-news.firebaseio.com/v0"


def get_item_by_id_sync(item_id: int) -> dict:
    try:
        response = httpx.get(f"{API_BASE_URL}/item/{item_id}.json", timeout=10)
        return response.json()
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}")
        return {}


def insert_item_sync(item: dict, session: Session):
    item_type = item.get("type")
    item["time"] = convert_unix_time(item["time"])
    item_id = item.get("id")

    if item_type == "story":
        obj_class = Story
    elif item_type == "comment":
        obj_class = Comment
    else:
        return None

    existing = session.get(obj_class, item_id)
    if existing:
        for key, value in item.items():
            if key in existing.model_fields:
                setattr(existing, key, value)
    else:
        obj = obj_class(**item)
        session.add(obj)
    session.commit()


def traverse_sync(item_id: int, session: Session, depth=1) -> list[dict]:
    item = get_item_by_id_sync(item_id)
    if not item:
        return []

    insert_item_sync(item, session)
    items = [item]

    if depth == 0:
        return items

    for kid_id in item.get("kids", []):
        items.extend(traverse_sync(kid_id, session, depth - 1))

    return items


def parse_with_threading(item_id: int, depth=2):
    print("Threading parser started")

    def worker(iid):
        with Session(sync_engine) as session:
            traverse_sync(iid, session, depth)

    threads = [Thread(target=worker, args=(item_id,)) for _ in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

def worker(iid, depth=2):
    with Session(sync_engine) as session:
        traverse_sync(iid, session, depth)


def parse_with_multiprocessing(item_id: int, depth=2):
    print("Multiprocessing parser started")

    processes = [Process(target=worker, args=(item_id,)) for _ in range(5)]  # example: 5 processes

    for p in processes:
        p.start()
    for p in processes:
        p.join()
