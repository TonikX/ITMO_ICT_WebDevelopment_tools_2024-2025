import aiohttp
import asyncio
from bs4 import BeautifulSoup
from db import get_session
from models import Trip


def load_urls(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


async def fetch(session, url):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            return await response.text(), url
    except Exception as e:
        print(f"[Fetch Error] {url}: {e}")
        return "", url


async def parse_and_save(html, url):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title_element = soup.find('h1', id='firstHeading')
        destination = title_element.get_text(strip=True) if title_element else "Неизвестно"

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
            description = "Описание отсутствует."

        with get_session() as session:
            session.add(Trip(destination=destination, description=description))
            session.commit()
        print(f"[Async] {destination} сохранена.")
    except Exception as e:
        print(f"[Async Error] {url}: {e}")


async def handle_url_async(chunk):
    async with aiohttp.ClientSession() as session:
        htmls = await asyncio.gather(*(fetch(session, url) for url in chunk))
        await asyncio.gather(*(parse_and_save(html, url) for html, url in htmls if html))


async def main():
    urls = load_urls("urls.txt")
    num_chunks = 5
    chunk_size = len(urls) // num_chunks
    chunks = [urls[i * chunk_size: (i + 1) * chunk_size] for i in range(num_chunks - 1)]
    chunks.append(urls[(num_chunks - 1) * chunk_size:])
    await asyncio.gather(*(handle_url_async(chunk) for chunk in chunks))


if __name__ == "__main__":
    import time

    start = time.time()
    asyncio.run(main())
    print(f"Время выполнения: {time.time() - start:.2f} сек")
