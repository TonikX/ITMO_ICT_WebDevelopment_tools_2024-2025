import json
import threading
import time
import requests
from bs4 import BeautifulSoup


def fetch_post_details(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    result = {"link": url, "title": None, "text": None}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["error"] = f"Request failed: {e}"
        return result

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.select_one("h1.content-title, div.content-title")
    if title_tag:
        result["title"] = title_tag.get_text(strip=True)

    paragraphs = soup.select("article.content__blocks p")
    text_blocks = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    result["text"] = "\n\n".join(text_blocks)

    return result


def worker(idx: int, total: int, url: str, output: list, lock: threading.Lock):
    print(f"[{idx}/{total}] Fetching: {url}")
    details = fetch_post_details(url)
    with lock:
        output.append(details)


if __name__ == "__main__":
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    detailed_posts = []
    lock = threading.Lock()
    threads = []

    total = len(posts)
    start_time = time.time()

    for idx, post in enumerate(posts, start=1):
        url = post.get("link")
        t = threading.Thread(
            target=worker,
            args=(idx, total, url, detailed_posts, lock),
            daemon=True
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    elapsed = time.time() - start_time
    batch_count = len(threads)

    output_data = {
        "meta": {
            "duration_seconds": round(elapsed, 2),
            "batches": batch_count
        },
        "posts": detailed_posts
    }

    with open("threads.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Done: parsed {len(detailed_posts)} posts in {round(elapsed,2)}s using {batch_count} threads")
