import multiprocessing as mp
import time
import traceback
from datetime import datetime
from urllib.parse import urljoin
import os

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, select, Session, create_engine

from parser import HABR_FLOWS, parse_and_save


from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("ENV переменная DATABASE_URL не задана")
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, echo=True, future=True)


SQLModel.metadata.create_all(engine)

app = FastAPI(title="Habr Parser")

class ParseRequest(BaseModel):
    flows: list[str] | None = None

class ParseResponse(BaseModel):
    message: str
    duration: float

@app.post("/parse", response_model=ParseResponse)
def run_parser(req: ParseRequest):
    flows = req.flows or HABR_FLOWS
    start = time.time()
    try:
        for flow in flows:
            parse_and_save(flow)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    duration = time.time() - start
    return ParseResponse(
        message=f"Parsed {len(flows)} flows",
        duration=duration
    )

