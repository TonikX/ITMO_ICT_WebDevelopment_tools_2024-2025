from fastapi import FastAPI, HTTPException
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List

app = FastAPI(title="Parser Service")

async def parse_url(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.title.string.strip() if soup.title else "No title"
                return title
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing {url}: {e}")

@app.post("/parse", response_model=List[dict])
async def parse_urls(urls: List[str]):
    tasks = [parse_url(url) for url in urls]
    titles = await asyncio.gather(*tasks, return_exceptions=True)
    results = [{"url": urls[i], "title": titles[i] if not isinstance(titles[i], Exception) else str(titles[i])} for i in range(len(urls))]
    return results