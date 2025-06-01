import aiohttp
from bs4 import BeautifulSoup

from db.db_saver import save_user_async, save_users


async def fetch(session, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    async with session.get(url, headers=headers, timeout=10, ssl=False) as response:
        text = await response.text()
        return url, text


async def parse_and_save(url):
    async with aiohttp.ClientSession() as session:
        url, html = await fetch(session, url)
        if html:
            await process_page_async(html)


def extract_text(tag, default=""):
    return tag.text.strip() if tag else default


def parse_user_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    user_blocks = soup.select("tr.cf-line")
    users = []

    for block in user_blocks:
        name_block = block.select_one("div.cf-title-card-new")
        location_span = block.select_one("span.text-10")
        name = extract_text(name_block).replace(location_span.text,
                                                "").strip() if name_block and location_span else extract_text(
            name_block)
        city = extract_text(location_span)

        category_block = block.select_one("a[data-id='qa-content-tr-td-cf-spec']")
        category = extract_text(category_block)

        users.append({
            "name": name,
            "email": f"{name.lower().replace(' ', '_')}@example.com",  # фиктивный email
            "password": "1234",  # фиктивный пароль
            "bio": f"Город: {city}. Специализация: {category}"
        })

    return users


def process_page(html, url=""):
    print(f"[INFO] Обрабатывается: {url}")

    users_data = parse_user_cards(html)
    if users_data:
        save_users(users_data)
    else:
        print("[INFO] Пользователи не найдены.")


async def process_page_async(html, url=""):
    print(f"[INFO] Обрабатывается: {url}")

    users_data = parse_user_cards(html)
    if users_data:
        await save_user_async(users_data)
    else:
        print("[INFO] Пользователи не найдены.")
