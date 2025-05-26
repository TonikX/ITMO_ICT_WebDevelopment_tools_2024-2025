urls = [
"https://habr.com/ru/articles/832678/",
"https://habr.com/ru/companies/yandex/articles/861538/",
"https://habr.com/ru/articles/847008/",
"https://habr.com/ru/articles/860828/",
"https://habr.com/ru/articles/833564/",
"https://habr.com/ru/companies/ruvds/articles/858212/",

]
import asyncio
import aiohttp
import time
from name_grabber import grab_name
from bs4 import BeautifulSoup

API_URL = "http://127.0.0.1:8000/auth/register"

async def grab_name(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            text = await response.text()

    soup = BeautifulSoup(text, "html.parser")
    name = soup.find_all("a", class_="tm-user-info__username")[0].text
    print(name)
    return name

async def create_user(session, username):
    user_data = {
        "username": username,
        "email": f"{username.strip()}@example.com",
        "password": "defaultpassword123"
    }
    try:
        async with session.post(API_URL, json=user_data) as response:
            text = await response.text()
            print(f"[{username}] Status: {response.status}")
            print(f"Response Text: {text}")

            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                json_response = await response.json()
                print("Parsed JSON:", json_response)
            else:
                print("Non-JSON response received")

    except Exception as e:
        print(f"Error creating {username} : {e}")

async def worker(session, url):
    try:
        username = await grab_name(url)
        await create_user(session, username)
    except Exception as e:
        print(f"Error processing {url}: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(worker(session, url))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")


#0.84