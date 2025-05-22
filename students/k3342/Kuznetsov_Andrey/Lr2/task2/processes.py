import json
import time
import math
import multiprocessing as mp
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


def worker_chunk(chunk):
    return [fetch_post_details(item["link"]) for item in chunk]


if __name__ == "__main__":
    with open("vc_money_posts.json", "r", encoding="utf-8") as f:
        posts = json.load(f)

    cpu_count = mp.cpu_count()
    total = len(posts)

    chunk_size = math.ceil(total / cpu_count)
    chunks = [posts[i:i + chunk_size] for i in range(0, total, chunk_size)]

    start_time = time.time()
    with mp.Pool(processes=cpu_count) as pool:
        results_per_chunk = pool.map(worker_chunk, chunks)

    elapsed = time.time() - start_time
    detailed_posts = [item for sublist in results_per_chunk for item in sublist]

    output_data = {
        "meta": {
            "duration_seconds": round(elapsed, 2),
            "batches": cpu_count
        },
        "posts": detailed_posts
    }

    with open("processes.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Done: parsed {len(detailed_posts)} posts in {round(elapsed, 2)}s "
          f"using {cpu_count} processes")
