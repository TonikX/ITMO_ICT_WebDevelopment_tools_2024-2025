import random
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)
import asyncio
from bs4 import BeautifulSoup
from config.secrets import ITMO_LOGIN, ITMO_PASSWORD

CONCURRENCY = 5


async def do_login_and_save_state(context):
    page = await context.new_page()
    await page.goto("https://my.itmo.ru/persons?p=1", wait_until="domcontentloaded", timeout=60000)

    await page.wait_for_selector("input#username", timeout=30000)
    await page.fill("input#username", ITMO_LOGIN)
    await page.fill("input#password", ITMO_PASSWORD)
    await page.click("input#kc-login")

    await page.wait_for_url("**/login/callback**", timeout=30000)

    await page.wait_for_selector("div#app-search-bar-container", timeout=30000)
    await context.storage_state(path="auth_state.json")
    await page.close()


async def fetch_and_parse(context, url):
    print(f"Fetching URL: {url}")
    users = []
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        try:
            await page.wait_for_selector("div.card.person-card", timeout=5000)
        except PlaywrightTimeoutError:
            return users

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        for card in soup.select("div.pb-3.col-xxl-3.col-md-6.col-xl-4.col-12"):
            username_span = card.select_one("span.badge.text-xs.align-middle.badge-primary-blue.badge-pill")
            username = username_span.get_text(strip=True) if username_span else None

            name_div = card.select_one("div.mt-1.font-weight-bold.text-black")
            name = name_div.get_text(strip=True) if name_div else None

            phone_span = None
            for span in card.select("span.text-black"):
                classes = span.get("class", [])
                if "contacts-email" not in classes:
                    phone_span = span
                    break
            phone = phone_span.get_text(strip=True) if phone_span else None

            email_span = card.select_one("span.contacts-email.max-lines-1.text-black")
            email = email_span.get_text(strip=True) if email_span else None

            users.append(
                {
                    "username": str(username),
                    "name": name,
                    "phone": phone,
                    "email": email,
                }
            )

    finally:
        await page.close()

    return users


async def sem_task(context, sem, url, idx):
    async with sem:
        try:
            data = await fetch_and_parse(context, url)
            return (url, data, None)
        except Exception as e:
            return (url, [], e)


async def parse(pages: int = 5):
    async with async_playwright() as p:
        urls = [f"https://my.itmo.ru/persons?p={random.randint(1, 100)}" for _ in range(pages)]

        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context()

        await do_login_and_save_state(context)

        await context.close()
        authed_context = await browser.new_context(storage_state="auth_state.json")

        sem = asyncio.Semaphore(CONCURRENCY)
        tasks = [asyncio.create_task(sem_task(authed_context, sem, url, idx)) for idx, url in enumerate(urls, start=1)]

        results = []
        for coro in asyncio.as_completed(tasks):
            url, data, err = await coro
            results.append((url, data))

        await authed_context.close()
        await browser.close()

    return results
