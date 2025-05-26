import asyncio

from fastapi import APIRouter, HTTPException
import requests
from ...Lr2.second.async_ import BookParser

router = APIRouter(prefix="/parsers", tags=["Parsers"])

@router.post("/parse")
def parse(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        parser = BookParser(url=url)
        asyncio.run(parser.run())
        return {"message": "Parsing completed"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))