from celery import Celery
import asyncio
import httpx

urls = ["https://books.toscrape.com/catalogue/category/books_1/index.html"]
celery_app = Celery(
    "tasks",
    broker="redis://book_redis:6379/0",
    backend="redis://book_redis:6379/0"
)


@celery_app.task(name="parse_url")
def parse_url_tasks(url: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_parse_url(url))

@celery_app.task(name="parse_all_urls")
def parse_all_urls():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_parse_all_urls())

async def _parse_url(url: str):
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as client:
            html_response = await client.get(url)
            parser_response = await client.post(
                "http://parser:9000/parse",
                json={"html": html_response.text}
            )
            return parser_response.json()
    except Exception as e:
        return {"error": str(e), "url": url}

async def _parse_all_urls():
    results = []
    for url in urls:
        result = await _parse_url(url)
        results.append(result)
    return results