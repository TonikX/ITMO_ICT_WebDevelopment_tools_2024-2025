import asyncio
import json
import asyncpg
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup

MAX_CONCURRENT = 300
DB_DSN = "postgresql://user:password@localhost:5432/yourdb"


async def fetch_post_details(session: ClientSession, url: str) -> dict:
    headers = {
        "User-Agent": (
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    result = {"link": url, "title": None, "text": None}
    try:
        async with session.get(url, headers=headers) as resp:
            resp.raise_for_status()
            html = await resp.text()
    except Exception as e:
        result["error"] = f"Request failed: {e}"
        return result

    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.select_one("h1.content-title, div.content-title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    paragraphs = soup.select("article.content__blocks p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    result["text"] = "\n\n".join(text_blocks)
    return result


async def save_to_db(pool, data):
    async with pool.acquire() as conn:
        try:
            await conn.execute("""
                INSERT INTO posts (url, title, text, error)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (url) DO NOTHING;
            """, data["link"], data.get("title"), data.get("text"), data.get("error"))
        except Exception as e:
            print(f"DB insert error for {data['link']}: {e}")


async def process_url(semaphore, pool, session, idx, total, url):
    async with semaphore:
        print(f"[{idx}/{total}] Fetching: {url}")
        data = await fetch_post_details(session, url)
        await save_to_db(pool, data)


async def main():
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    timeout = ClientTimeout(total=60)

    pool = await asyncpg.create_pool(dsn=DB_DSN, min_size=5, max_size=MAX_CONCURRENT)

    async with ClientSession(timeout=timeout) as session:
        tasks = [
            asyncio.create_task(
                process_url(semaphore, pool, session, idx, len(posts), post["link"])
            )
            for idx, post in enumerate(posts, start=1)
        ]
        await asyncio.gather(*tasks)

    await pool.close()
    print("All posts written to database.")


if __name__ == "__main__":
    asyncio.run(main())
