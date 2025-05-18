from bs4 import BeautifulSoup
import requests
from app.db import get_session
from app.models import Trip


def parse_and_save_single(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    title_element = soup.find('h1', id='firstHeading')
    destination = title_element.get_text(strip=True) if title_element else "Unknown"

    description = ""
    content_div = soup.find('div', class_='mw-parser-output')
    if content_div:
        for p in content_div.find_all('p'):
            text = p.get_text(strip=True)
            if text:
                description += text + " "
                if len(description) > 1000:
                    break
    if not description.strip():
        description = "Description not found"

    try:
        with get_session() as session:
            trip = Trip(destination=destination, description=description.strip())
            session.add(trip)
            session.commit()
            print("Commit successful")
    except Exception as e:
        print(f"Error saving to DB: {e}")
        raise

    return destination
