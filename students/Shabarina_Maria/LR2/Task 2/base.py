import requests
from bs4 import BeautifulSoup


def get_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", class_="article__content")
    if not content_div:
        return "Нет основного текста"
    paragraphs = content_div.find_all("p")
    text = "\n".join(p.get_text(strip=True) for p in paragraphs)
    return text


def get_articles():
    response = requests.get("https://matchtv.ru/news")
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", class_="node-news-list__item")
    return articles


def get_topic(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    topic_elem = soup.find_all("li", class_="credits__item")
    return topic_elem[1].get_text(strip=True) if topic_elem else None
