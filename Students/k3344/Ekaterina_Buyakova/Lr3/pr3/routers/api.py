from urllib.parse import urlparse

from celery_app import parse_and_save
from core import settings
from fastapi import APIRouter

router = APIRouter()


def is_valid_url(url: str):
    result = urlparse(url)
    return all([result.scheme in ('http', 'https'), result.netloc])


@router.get("/")
def parse_url(url: str = ""):
    if not is_valid_url(url):
        return {"message": "Invalid URL"}
    parse_and_save.delay(url)
    return {"message": "Task created", "url": url}
