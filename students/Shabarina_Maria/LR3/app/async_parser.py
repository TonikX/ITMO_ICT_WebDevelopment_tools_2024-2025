import asyncio
import time
import aiohttp
from app.connection import get_session, init_db
from app.models import News
from bs4 import BeautifulSoup


async def get_article_text(url, session):
    try:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            content_div = soup.find("div", class_="article__content")
            if not content_div:
                return "Нет основного текста"
            paragraphs = content_div.find_all("p")
            return "\n".join(p.get_text(strip=True) for p in paragraphs)
    except Exception as e:
        print(f"[Async Error] {url}: {e}")
        return "Ошибка при получении текста"


async def get_articles():
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get("https://matchtv.ru/news") as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                return soup.find_all("a", class_="node-news-list__item")
        except Exception as e:
            print(f"[Async Error] get_articles: {e}")
            return []


async def parse_and_save(article, session):
    try:
        href = article.get("href")
        full_url = "https://matchtv.ru" + href
        title_elem = article.find("div", class_="node-news-list__title")
        title = title_elem.get_text(strip=True) if title_elem else "Нет заголовка"
        topic_elem = article.find_all("li", class_="credits__item")
        topic = topic_elem[1].get_text(strip=True) if topic_elem else "Нет темы"

        text = await get_article_text(full_url, session)
        result = {
            "url": full_url,
            "title": title,
            "topic": topic,
            "text": text
        }

        with get_session() as db_session:
            new = News.model_validate(result)
            db_session.add(new)
            db_session.commit()

        print(f"[Task] {title} сохранена")
    except Exception as e:
        print(f"[Task Error] № {title}: {e}")


async def handle_article_async(chunk, session):
    tasks = [parse_and_save(article, session) for article in chunk]
    await asyncio.gather(*tasks)


async def main():
    articles = await get_articles()
    num_tasks = 4
    step = len(articles) // num_tasks

    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        for i in range(num_tasks):
            start = i * step
            if i != num_tasks - 1:
                end = (i + 1) * step + 1
            else:
                end = len(articles) + 1
            await handle_article_async(articles[start:end], session)


async def run_parser():
    init_db()
    start = time.time()
    await main()
    print(f"Время выполнения: {time.time() - start:.2f} сек")
    print("Парсинг завершён!")

