import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from models import *
import ssl

db_url = 'postgresql+asyncpg://dbuser:12345678@localhost:25432/db'
async_engine = create_async_engine(db_url, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def parse_and_save(session: aiohttp.ClientSession, url: str):
    async with session.get(url, timeout=10, ssl=ssl_context) as resp:
        resp.raise_for_status()
        html = await resp.text()

    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('h2', class_='problem_title').text.strip()

    text = ''
    texts = soup.find_all('div', class_='problem_par_normal')
    for t in texts:
        text += t.text.strip() + '\n'

    async with AsyncSessionLocal() as db:
        async with db.begin():
            task = Task(
                title=title,
                description=text,
            )
            db.add(task)