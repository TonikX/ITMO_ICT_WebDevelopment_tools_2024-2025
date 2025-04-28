import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
import time
from utils.db_utils import init_db, save_page

async def fetch_page(session, url):
    start_time = time.time()
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as http_session:
            async with http_session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    end_time = time.time()
                    return url, html, end_time - start_time
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
    return url, None, None

async def parse_pages(urls):
    """Асинхронно парсит список URL."""
    session = init_db()
    results = []
    
    # Создаем SSL контекст с отключенной проверкой
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as http_session:
        tasks = [fetch_page(http_session, url) for url in urls]
        fetch_results = await asyncio.gather(*tasks)
        
        for url, html, load_time in fetch_results:
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string if soup.title else "Без заголовка"
                content = soup.get_text()[:1000]  # Сохраняем первые 1000 символов
                
                save_page(
                    session=session,
                    url=url,
                    title=title,
                    content=content,
                    parsing_method="async",
                    parsing_time=load_time
                )
                results.append({
                    'url': url,
                    'title': title,
                    'content': content,
                    'parsing_time': load_time
                })
    
    session.close()
    return results

async def main():
    # Пример списка URL для парсинга
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
    ]
    
    await parse_pages(urls)

if __name__ == "__main__":
    asyncio.run(main()) 