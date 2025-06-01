import aiohttp
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Query

from db import save_to_db
from parse_utils import parse_title_author, fetch

app = FastAPI()


@app.get("/parse")
async def parse_url(url: str = Query(...)):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
    if not html:
        raise HTTPException(500, "Failed to fetch page")

    soup = BeautifulSoup(html, "html.parser")
    full_title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
    title, author = parse_title_author(full_title)

    try:
        await save_to_db(url, title, author)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving to DB: {e}")

    return {
        "url": url,
        "title": title,
        "author": author
    }
