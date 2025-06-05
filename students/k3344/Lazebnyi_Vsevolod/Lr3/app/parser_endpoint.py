from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List
from celery.app.control import Inspect
from .celery_worker import celery_app
from app.tasks import celery_app
from app.async_parser import process_asset
import asyncio

parser_router = APIRouter(prefix="/api", tags=["parser"])

class AssetRequest(BaseModel):
    name: str
    ticker: str

class MultipleAssetRequest(BaseModel):
    tickers: str

ASSET_MAPPING = [
    {"name": "Apple Inc.", "ticker": "AAPL"},
    {"name": "Tesla, Inc.", "ticker": "TSLA"},
    {"name": "Sberbank of Russia", "ticker": "SBER.ME"},
    {"name": "Brent Crude Oil", "ticker": "BZ=F"},
    {"name": "WTI Crude Oil", "ticker": "CL=F"}
]

def get_asset_by_ticker(ticker: str):
    for asset in ASSET_MAPPING:
        if asset['ticker'].upper() == ticker.strip().upper():
            return asset
    return {"name": f"Unknown ({ticker})", "ticker": ticker}

@parser_router.post("/parse/sync")
async def parse_sync(asset: AssetRequest):
    try:
        await process_asset({"name": asset.name, "ticker": asset.ticker})
        return {"message": f"Parsing completed for {asset.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@parser_router.post("/parse/async")
async def parse_async(asset: AssetRequest):
    try:
        task = celery_app.send_task("parse_asset", args=[{"name": asset.name, "ticker": asset.ticker}])
        return {"task_id": task.id, "message": f"Parsing task started for {asset.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@parser_router.post("/parse/multiple/sync")
async def parse_multiple_sync(request: MultipleAssetRequest):
    try:
        tickers = [ticker.strip() for ticker in request.tickers.split(",") if ticker.strip()]
        results = []
        for ticker in tickers:
            asset = get_asset_by_ticker(ticker)
            await process_asset(asset)
            results.append({"ticker": ticker, "name": asset["name"], "status": "completed"})
        return {"message": f"Parsing completed for {len(tickers)} assets", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@parser_router.post("/parse/multiple/async")
async def parse_multiple_async(request: MultipleAssetRequest):
    try:
        tickers = [ticker.strip() for ticker in request.tickers.split(",") if ticker.strip()]
        task_ids = []
        for ticker in tickers:
            asset = get_asset_by_ticker(ticker)
            task = celery_app.send_task("parse_asset", args=[asset])
            task_ids.append({"ticker": ticker, "name": asset["name"], "task_id": task.id})
        return {"message": f"Parsing tasks started for {len(tickers)} assets", "tasks": task_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@parser_router.get("/celery-status")
def celery_status():
    inspector = celery_app.control.inspect()
    active = inspector.active()
    reserved = inspector.reserved()
    scheduled = inspector.scheduled()
    return {
        "active": active,
        "reserved": reserved,
        "scheduled": scheduled
    } # AAPL, TSLA, BZ=F, CL=F, SBER.ME, MSFT, GOOG, AMZN, FB