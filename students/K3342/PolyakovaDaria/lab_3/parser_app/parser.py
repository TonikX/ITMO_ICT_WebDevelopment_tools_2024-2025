from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()


class URLRequest(BaseModel):
    url: str


@app.post("/parse")
def parse(request: URLRequest):
    try:
        response = requests.get(request.url, timeout=30)
        response.raise_for_status()
        html = response.text
        return {
            "message": "Parsing completed successfully!",
            "content_size": len(html),
            "content": html
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
