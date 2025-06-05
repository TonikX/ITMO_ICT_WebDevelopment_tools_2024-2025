import time
import yfinance as yf
import pandas as pd
from connection import init_db, get_session
from models import StockData

def fetch_historical_data(asset):
    ticker = asset['ticker']
    stock = yf.Ticker(ticker)
    df = stock.history(start="2023-01-01", end="2023-12-31")
    if df.empty:
        return asset, None
    data = df.reset_index().to_dict('records')
    return asset, data

def save_data_to_db(asset, data):
    if not data:
        return
    records = []
    for entry in data:
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
    with get_session() as db_session:
        for record in records:
            db_session.add(record)
        db_session.commit()

def process_asset(asset):
    asset, data = fetch_historical_data(asset)
    save_data_to_db(asset, data)

def main():
    assets_to_search = [
        {"name": "Apple Inc.", "ticker": "AAPL"},
        {"name": "Tesla, Inc.", "ticker": "TSLA"},
        {"name": "Sberbank of Russia", "ticker": "SBER.ME"},
        {"name": "Brent Crude Oil", "ticker": "BZ=F"},
        {"name": "WTI Crude Oil", "ticker": "CL=F"}
    ]
    for asset in assets_to_search:
        process_asset(asset)

if __name__ == "__main__":
    init_db()
    start = time.time()
    main()
    print(f"Time: {time.time() - start:.2f} seconds")