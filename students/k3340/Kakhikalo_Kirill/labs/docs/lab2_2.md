Результаты выполнения:

| Тип             | Время выполнения, с |
|-----------------|---------------------|
| multithreading  | 0.34                |
| multiprocessing | 1.29                |
| asyncio         | 0.36                |

При активном взаимодействии с IO (сетевые запросы) multithreading и asyncio одинаково эффективны,
так как в обоих случаях большую часть времени заняло бы выполнение запросов.
Выполнение запросов не блокирует интерперататор и поэтому оба варианта работают эффективно.
Вариант с мультипроцессингом неэффективен, так как имеет слишком большой оверхед на создание.

Вариант с мультпроцессингом стал бы эффективен при значительном увеличении количества парсящихся сайтов,
на порядки больше.

Для выполнения задачи я получаю html код 3 страниц, которые разделены между 3 исполнителями,
получаю из страниц название человека и его состояние, регистрирую на человека аккаунт в моей системе,
полчую его токен, создаю ему счёт и транзакцию с начальным уровнем богатства.

Листинг кода для asyncio:

```python
import asyncio
import aiohttp
import time

BASE_URL = "http://127.0.0.1:8010"


async def create_user(session, username, email, password):
    payload = {
        "username": username,
        "email": email,
        "password": password
    }

    async with session.post(f"{BASE_URL}/users", json=payload) as resp:
        resp.raise_for_status()
        return await resp.json()


async def get_token(session, username, password):
    data = {
        "username": username,
        "password": password
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with session.post(f"{BASE_URL}/token", data=data, headers=headers) as resp:
        resp.raise_for_status()
        token_data = await resp.json()
        return token_data["access_token"]


async def create_account(session, token, name, balance, currency):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "name": name,
        "balance": balance,
        "currency": currency
    }

    async with session.post(f"{BASE_URL}/accounts", json=payload, headers=headers) as resp:
        resp.raise_for_status()
        return await resp.json()


async def create_transaction(session, token, account_id, amount, category_id):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "account_id": account_id,
        "amount": amount,
        "category_id": category_id,
        "description": "Initial wealth transfer"
    }

    async with session.post(f"{BASE_URL}/accounts/{account_id}/transactions", json=payload, headers=headers) as resp:
        resp.raise_for_status()
        return await resp.json()


async def fetch(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
    }
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.text()


async def parse_and_save_data_single(url):
    async with aiohttp.ClientSession() as session:
        data = await fetch(session, url)
        title = data.split('<title itemprop="headline">')[1].split('</title>')[0]
        wealth = data.split('profile-info__item-value">$')[1].split('B</div>')[0]
        wealth = wealth.replace('.', '') if wealth else '0'
        wealth = int(wealth)
        await create_user(session, title.replace(' ', '_').lower(), f"{title.replace(' ', '_').lower()}@example.com", "12345678")
        token = await get_token(session, title.replace(' ', '_').lower(), "12345678")
        account = await create_account(session, token, title, wealth, "USD")
        await create_transaction(session, token, account['id'], wealth, "730864ac-e174-4996-99c1-1caf8b934202")

async def parse_and_save_data(urls):
    tasks = [parse_and_save_data_single(url) for url in urls]
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*tasks)


start_time = time.perf_counter()
asyncio.run(parse_and_save_data(['https://www.forbes.com/profile/elon-musk/?list=rtb/', 'https://www.forbes.com/profile/mark-zuckerberg/?list=rtb/', 'https://www.forbes.com/profile/jeff-bezos/?list=rtb/']))
end_time = time.perf_counter()
print(f"{end_time - start_time} seconds")
#0.3639050999772735 seconds
```