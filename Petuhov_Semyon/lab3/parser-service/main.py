from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from parser import parse_books_from_url

app = FastAPI()

class ParseRequest(BaseModel):
    url: str
    genre: str

@app.post("/parse", response_model=List[dict])
async def parse_endpoint(req: ParseRequest):
    try:
        books = parse_books_from_url(req.url, req.genre)
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
