import re
from datetime import datetime

import aiohttp
import requests
from bs4 import BeautifulSoup

from common.db import save_task_async, save_task


async def fetch(session, url):
    async with session.get(url, timeout=10, ssl=False) as response:
        text = await response.text()
        return url, text


async def parse_and_save_async(url):
    async with aiohttp.ClientSession() as session:
        url, html = await fetch(session, url)
        if html:
            await process_page_async(html)


def extract_article_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.match(r"^/[\w\-]+/$", href) or href.startswith("https://lifehacker.ru/"):
            full_url = href if href.startswith("http") else f"https://lifehacker.ru{href}"
            links.append(full_url)

    return list(set(links))

def process_page(html):
    article_links = extract_article_links(html)
    if not article_links:
        print("[INFO] Ссылки на статьи не найдены.")
    for link in article_links:
        task_data = {
            "title": "Новая статья",
            "description": f"Ссылка: {link}",
            "due_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "image_url": None,
            "owner_id": 1,
            "priority": "high",
            "status": "new"
        }
        save_task(task_data)

async def process_page_async(html):
    article_links = extract_article_links(html)
    if not article_links:
        print("[INFO] Ссылки на статьи не найдены.")
    for link in article_links:
        task_data = {
            "title": "Новая статья",
            "description": f"Ссылка: {link}",
            "due_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "image_url": None,
            "owner_id": 1,
            "priority": "high",
            "status": "new"
        }
        await save_task_async(task_data)
