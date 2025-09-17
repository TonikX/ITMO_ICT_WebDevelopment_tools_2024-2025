import re
import requests
from urllib.parse import urljoin
from selectolax.parser import HTMLParser

FINANCE_URL = "https://www.kommersant.ru/finance?from=burger"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def _first(tree, selector, attr=None):
    node = tree.css(selector)
    if not node:
        return ""
    return node[0].attributes.get(attr, "").strip() if attr else node[0].text().strip()

def get_articles(limit=30):
    resp = requests.get(FINANCE_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return extract_doc_links(resp.text, FINANCE_URL, limit)

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

def get_article_text(url):
    article_data = parse_article(url)
    return article_data["text"]

def get_title(url):
    article_data = parse_article(url)
    return article_data["title"]

def get_topic(url):
    article_data = parse_article(url)
    return article_data["section"]

def parse_article(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    tree = HTMLParser(resp.text)
    
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