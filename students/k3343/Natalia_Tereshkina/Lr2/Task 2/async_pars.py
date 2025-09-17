import asyncio
import time
import re
import json
from urllib.parse import urljoin
import httpx
from selectolax.parser import HTMLParser
from connection import get_session  
from models import News

FINANCE_URL = "https://www.kommersant.ru/finance?from=burger"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def _first(tree, selector, attr=None):
    node = tree.css(selector)
    if not node:
        return ""
    return node[0].attributes.get(attr, "").strip() if attr else node[0].text().strip()

def extract_doc_links(html, base, limit):
    tree = HTMLParser(html)
    out, seen = [], set()
    for a in tree.css('a[href]'):
        href = a.attributes.get('href', '')
        if not href:
            continue
        url = urljoin(base, 'https:' + href if href.startswith('//') else href).split('?')[0]
        if re.search(r"/doc/\d+", url) and url not in seen:
            seen.add(url)
            out.append(url)
        if len(out) >= limit:
            break
    return out

def parse_article(html, url):
    tree = HTMLParser(html)
    title = (_first(tree, 'meta[property="og:title"]', 'content')
            or _first(tree, 'h1')
            or _first(tree, 'title')) or "Нет заголовка"
    published = (_first(tree, 'meta[property="article:published_time"]', 'content')
            or _first(tree, 'time[datetime]', 'datetime')
            or _first(tree, 'time'))
    section = (_first(tree, 'meta[property="article:section"]', 'content')
            or _first(tree, 'nav a[href*="/finance"]')
            or _first(tree, 'nav a[href*="/money"]'))
    paragraphs = []
    for sel in [
        'article p', 'div[itemprop="articleBody"] p', 'section[itemprop="articleBody"] p',
        'div[class*="article"] p', 'div[class*="content"] p', 'p']:
        for p in tree.css(sel):
            t = p.text().strip()
            if len(t) >= 40 and not re.match(r"^(Фото|Видео|Читайте также)[:]", t, re.I):
                paragraphs.append(t)
        if paragraphs:
            break
    return {
        "url": url,
        "title": title,
        "published": published or "",
        "section": section or "",
        "text": "\n\n".join(paragraphs) or "Нет основного текста"
    }

async def fetch(client, url):
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    return r.text

async def save_article_to_db(item):
    def _save():
        try:
            with get_session() as session:
                session.add(News.model_validate(item))
                session.commit()
            return True
        except Exception:
            return False
    return await asyncio.to_thread(_save)

async def main(limit=30, concurrency=10):
    start = time.time()
    saved = 0
    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
        listing_html = await fetch(client, FINANCE_URL)
        urls = extract_doc_links(listing_html, FINANCE_URL, limit)
        sem = asyncio.Semaphore(concurrency)
        async def get_and_save(u):
            nonlocal saved
            async with sem:
                item = parse_article(await fetch(client, u), u)
                ok = await save_article_to_db({
                    "url": item["url"],
                    "title": item["title"],
                    "topic": item.get("section") or "Нет темы",
                    "text": item["text"]
                })
                if ok: saved += 1
        await asyncio.gather(*(get_and_save(u) for u in urls))
    print(f"Готово: {saved} новостей сохранено, время: {time.time()-start:.2f} сек")

if __name__ == "__main__":
    asyncio.run(main())