import re
import requests
from bs4 import BeautifulSoup
from finances_lab2.task2.common.db import save_task
from datetime import datetime

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

def parse_and_save(url_list):
    for url in url_list:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"[INFO] Обрабатывается {url}")
        process_page(response.text)
