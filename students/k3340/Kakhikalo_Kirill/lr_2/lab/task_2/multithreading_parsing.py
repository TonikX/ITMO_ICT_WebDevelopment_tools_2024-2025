import time
import requests
import threading

BASE_URL = "http://127.0.0.1:8010"

def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) "
                      "Gecko/20100101 Firefox/138.0"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def create_user_sync(username, email, password):
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/users", json=payload)
    resp.raise_for_status()
    return resp.json()

def get_token_sync(username, password):
    data = {
        "username": username,
        "password": password
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{BASE_URL}/token", data=data, headers=headers)
    resp.raise_for_status()
    return resp.json()["access_token"]

def create_account_sync(token, name, balance, currency):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": name,
        "balance": balance,
        "currency": currency
    }
    resp = requests.post(f"{BASE_URL}/accounts", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def create_transaction_sync(token, account_id, amount, category_id):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "account_id": account_id,
        "amount": amount,
        "category_id": category_id,
        "description": "Initial wealth transfer"
    }
    resp = requests.post(f"{BASE_URL}/accounts/{account_id}/transactions", json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def parse_and_save_data_single(url: str):
    html = fetch_html(url)
    title = html.split('<title itemprop="headline">')[1].split('</title>')[0]
    wealth = html.split('profile-info__item-value">$')[1].split('B</div>')[0]
    wealth = wealth.replace('.', '') if wealth else '0'
    wealth = int(wealth)

    username = title.replace(" ", "_").lower()
    email = f"{username}@example.com"
    password = "12345678"

    create_user_sync(username, email, password)
    token = get_token_sync(username, password)
    account = create_account_sync(token, title, wealth, "USD")
    category_id = "730864ac-e174-4996-99c1-1caf8b934202"
    create_transaction_sync(token, account["id"], wealth, category_id)

def parse_and_save_data(urls):
    threads = []
    for url in urls:
        thread = threading.Thread(target=parse_and_save_data_single, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

urls = [
    "https://www.forbes.com/profile/elon-musk/?list=rtb/",
    "https://www.forbes.com/profile/mark-zuckerberg/?list=rtb/",
    "https://www.forbes.com/profile/jeff-bezos/?list=rtb/"
]

if __name__ == '__main__':
    start_time = time.perf_counter()
    parse_and_save_data(urls)
    end_time = time.perf_counter()
    print(f"{end_time - start_time} seconds")

#0.34367170004406944 seconds