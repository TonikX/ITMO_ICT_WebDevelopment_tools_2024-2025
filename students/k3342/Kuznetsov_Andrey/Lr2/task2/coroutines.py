import json
import asyncio
import time
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup

MAX_CONCURRENT = 500


async def fetch_post_details(session: ClientSession, url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
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


async def bound_fetch(semaphore, session, idx, total, url, output):
    async with semaphore:
        print(f"[{idx}/{total}] Fetching: {url}")
        details = await fetch_post_details(session, url)
        output.append(details)


async def main():
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    total = len(posts)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    detailed_posts = []
    timeout = ClientTimeout(total=60)

    start = time.monotonic()
    async with ClientSession(timeout=timeout) as session:
        tasks = []
        for idx, post in enumerate(posts, start=1):
            url = post.get("link")
            tasks.append(
                asyncio.create_task(
                    bound_fetch(semaphore, session, idx, total, url, detailed_posts)
                )
            )
        await asyncio.gather(*tasks)
    elapsed = time.monotonic() - start

    output_data = {
        "meta": {
            "duration_seconds": round(elapsed, 2),
            "batches": total
        },
        "posts": detailed_posts
    }
    with open("coroutines.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Done: parsed {len(detailed_posts)} posts in {round(elapsed,2)}s using concurrency={MAX_CONCURRENT}")

if __name__ == "__main__":
    asyncio.run(main())
