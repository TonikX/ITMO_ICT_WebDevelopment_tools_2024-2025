from celery_worker import celery_app
from parser import parse_and_save
from typing import List

@celery_app.task
def run_parser_task(urls: List[str], user_id: int, category_name: str):
    results = []
    for url in urls:
        result = parse_and_save(url, user_id, category_name)
        results.append(result)
    return f"Parsed {len(results)} URLs for user {user_id} in category '{category_name}'"
