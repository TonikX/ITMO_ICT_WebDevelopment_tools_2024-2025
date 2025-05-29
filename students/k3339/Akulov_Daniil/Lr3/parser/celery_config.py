from celery import Celery
from parser import parse_and_save_page
import requests

celery_app = Celery("parser", broker='redis://redis:6379/0', backend='redis://redis:6379/0')


@celery_app.task(name="parse_from_url")
def parse_from_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        hackathon = parse_and_save_page(response.text)
    except requests.RequestException as e:
        print(f"Error processing {url}: {e}")