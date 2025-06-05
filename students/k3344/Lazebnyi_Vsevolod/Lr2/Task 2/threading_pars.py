import time
import yfinance as yf
import pandas as pd
import threading
from connection import init_db, get_session
from models import StockData

def fetch_historical_data(asset):
    ticker = asset['ticker']
    stock = yf.Ticker(ticker)
    df = stock.history(start="2023-01-01", end="2024-12-31")
    if df.empty:
        return asset, None
    data = df.reset_index().to_dict('records')
    return asset, data

def save_data_to_db(asset, data):
    if not data:
        print(f"No data to save for {asset['name']} ({asset['ticker']})")
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
    print(f"Saved {len(records)} for {asset['name']} ({asset['ticker']})")

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
    threads = []
    for asset in assets_to_search:
        thread = threading.Thread(target=process_asset, args=(asset,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    init_db()
    start = time.time()
    main()
    print(f"Время вып: {time.time() - start:.2f} секунд")