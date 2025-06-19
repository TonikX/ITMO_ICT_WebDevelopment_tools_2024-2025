from celery_worker.celery_app import celery_app
from bs4 import BeautifulSoup
import requests
@celery_app.task
def  parse_url(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Send a GET request to fetch the page content
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Will raise an exception if there's an error in the request

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find_all("a", class_="tm-user-info__username")[0].text
    return name
