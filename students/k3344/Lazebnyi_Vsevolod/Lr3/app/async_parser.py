import asyncio
import yfinance as yf
import pandas as pd
from app.connection import get_session
from app.models import StockData

async def fetch_historical_data(asset):
    try:
        ticker = asset['ticker']
        stock = yf.Ticker(ticker)
        df = stock.history(start="2023-01-01", end="2024-12-31")
        if df.empty:
            return asset, None
        data = df.reset_index().to_dict('records')
        return asset, data
    except Exception:
        return asset, None

async def save_data_to_db(asset, data):
    if not data:
        print(f"No data to save for {asset['name']} ({asset['ticker']})")
        return
    records = []
    for entry in data:
        try:
            date_obj = entry['Date'].date() if isinstance(entry['Date'], pd.Timestamp) else entry['Date']
            record = StockData(
                asset_name=asset['name'],
                ticker=asset['ticker'],
                investing_id=0,
                date=date_obj,
                open_price=float(entry['Open']),
                high_price=float(entry['High']),
                low_price=float(entry['Low']),
                close_price=float(entry['Close']),
                volume=int(entry['Volume']) if 'Volume' in entry else 0
            )
            records.append(record)
        except (ValueError, KeyError, TypeError):
            continue
    try:
        with get_session() as db_session:
            for record in records:
                db_session.add(record)
            db_session.commit()
    except Exception as e:
        print(f"Failed to save data {asset['name']} ({asset['ticker']}) {e}")

async def process_asset(asset):
    _, data = await fetch_historical_data(asset)
    await save_data_to_db(asset, data)