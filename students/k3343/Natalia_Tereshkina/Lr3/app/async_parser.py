import asyncio
import re
import time
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser

from app.connection import get_async_session
from app.tables import NewsArticle

FINANCE_URL = "https://www.kommersant.ru/finance?from=burger"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def _first(tree, selector, attr=None):
    nodes = tree.css(selector)
    if not nodes:
        return ""
    return nodes[0].attributes.get(attr, "").strip() if attr else nodes[0].text().strip()

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
        'div[class*="article"] p', 'div[class*="content"] p', 'p'
    ]:
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
    r = await client.get(url, follow_redirects=True, timeout=20)
    r.raise_for_status()
    return r.text

async def save_article_to_db(item):
    try:
        async with await get_async_session() as session:
            news = NewsArticle(
                url=item["url"],
                title=item["title"],
                topic=item.get("section") or "Нет темы",
                text=item["text"]
            )
            session.add(news)
            await session.commit()
            return True
    except Exception as e:
        print('DB ERROR:', e)
        return False

async def parse_news(count: int) -> dict:
    t0 = time.time()
    saved = 0
    async with httpx.AsyncClient(headers=HEADERS, timeout=20) as client:
        html = await fetch(client, FINANCE_URL)
        urls = extract_doc_links(html, FINANCE_URL, count)
        sem = asyncio.Semaphore(10)
        async def get_and_save(u):
            nonlocal saved
            async with sem:
                item = parse_article(await fetch(client, u), u)
                ok = await save_article_to_db(item)
                if ok:
                    saved += 1
        await asyncio.gather(*(get_and_save(u) for u in urls))
    return {
        "message": f"Готово: {saved} новостей сохранено, время: {time.time()-t0:.2f} сек",
        "requested": count,
        "saved": saved,
    }