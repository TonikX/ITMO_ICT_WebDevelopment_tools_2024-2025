import os
import sys
import traceback
from sqlalchemy import text
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy.orm import Session

from .db import engine, Base, get_db
from .models import Article, ArticleHub, Hub

class ParseRequest(BaseModel):
    flows: list[str]

class ParseResponse(BaseModel):
    message: str

PARSER_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001/parse")

app = FastAPI(title="Main API Service")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    value = db.execute(text("SELECT 1")).scalar()
    return {"status": "ok" if value == 1 else "fail"}

@app.post("/parse", response_model=ParseResponse)
def parse_url(req: ParseRequest):
    try:
        resp = requests.post(PARSER_URL, json={"flows": req.flows}, timeout=60)
        resp.raise_for_status()
        return ParseResponse(**resp.json())
    except Exception:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail={"error": "Parser service error", "trace": tb}
        )


@app.get("/articles/{article_id}", response_model=Article)
def read_article(article_id: int, db: Session = Depends(get_db)):
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(404, "Article not found")
    return article
