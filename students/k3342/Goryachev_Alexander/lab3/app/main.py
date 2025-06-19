from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
import aiohttp
from celery_worker.tasks import parse_url


app = FastAPI()

async def grab_name(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

    soup = BeautifulSoup(text, "html.parser")
    name = soup.find_all("a", class_="tm-user-info__username")[0].text
    return name

@app.get("/parse")
async def parse(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        # Вызов парсера
        result = await grab_name(url)
        return result
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/celery-parse")
def run_parse_task(data: dict):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    task = parse_url.delay(url)
    return {"task_id": task.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)