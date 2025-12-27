import os
import multiprocessing as mp
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Session, create_engine, select

from models import Article, Hub, ArticleHub

DATABASE_URL = os.getenv("DATABASE_URL")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

HABR_FLOWS = [
    "https://habr.com/ru/flows/develop/articles/",
    "https://habr.com/ru/flows/admin/articles/",
    "https://habr.com/ru/flows/popsci/articles/"
]


app = FastAPI(title="Habr Parser Service")

class ParseRequest(BaseModel):
    flows: list[str] | None = Field(
        default=None,
        description="Список URL-FLOWS для парсинга; если не указан, берутся все по умолчанию"
    )

class ParseResponse(BaseModel):
    message: str

def parse_and_save(flow_url: str):
    print(f"→ [Process {mp.current_process().name}] Parsing {flow_url}")
    try:
        resp = requests.get(
            flow_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"  ✖ [Process {mp.current_process().name}] Fetch error: {e}")
        return

    soup = BeautifulSoup(resp.text, "html.parser")
    snippets = soup.select("article.tm-articles-list__item")
    print(f"  • [Process {mp.current_process().name}] Snippets found: {len(snippets)}")

    with Session(engine) as session:
        for snip in snippets:
            a_title = snip.select_one("h2.tm-title a.tm-title__link")
            if not a_title:
                continue
            title = a_title.get_text(strip=True)
            link = urljoin(flow_url, a_title["href"])

            time_tag = snip.select_one("time[datetime]")
            iso = time_tag["datetime"]
            if iso.endswith("Z"):
                iso = iso[:-1] + "+00:00"
            published = datetime.fromisoformat(iso)

            author_el = snip.select_one("a.tm-user-info__username")
            author = author_el.get_text(strip=True) if author_el else "unknown"

            vc_el = snip.select_one("span.tm-icon-counter__value[title]")
            view_count = int(vc_el["title"]) if vc_el and vc_el.has_attr("title") else 0


            article = Article(
                title=title,
                url=link,
                published_at=published,
                flow=flow_url.rstrip("/").split("/")[-2],
                author=author,
                view_count=view_count,
            )
            session.add(article)
            session.commit()

            for hub_name in {h.get_text(strip=True) for h in snip.select("a.tm-publication-hub__link span")}:
                existing = session.exec(select(Hub).where(Hub.name == hub_name)).one_or_none()
                if not existing:
                    hub = Hub(name=hub_name)
                    session.add(hub)
                    session.commit()
                else:
                    hub = existing
                session.add(ArticleHub(article_id=article.id, hub_id=hub.id))
            session.commit()

            print(f"  • [Process {mp.current_process().name}] '{title[:30]}…' by {author}, views={view_count}")

    print(f"✔ [Process {mp.current_process().name}] Done {flow_url}\n")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/parse", response_model=ParseResponse)
def parse_endpoint(req: ParseRequest):
    flows = req.flows or HABR_FLOWS
    try:
        start = time.time()
        with mp.Pool(mp.cpu_count()) as pool:
            pool.map(parse_and_save, flows)
        elapsed = time.time() - start
        return ParseResponse(message=f"Parsing completed in {elapsed:.2f}s on flows: {flows}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
