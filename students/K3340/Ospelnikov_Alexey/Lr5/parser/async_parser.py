import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from sqlalchemy.sql import insert
from sqlalchemy import create_engine, MetaData, Table, select


async def save(engine, task_table, tasks):
    
    with engine.connect() as connection:
        try:
            for task_i in tasks:
                stmt = insert(task_table).values(
                    name=task_i,
                    deadline='2026-01-01 00:00:00.000',
                    status='in_progress',
                    priority='medium',
                    created_by=0
                )
                
                result = connection.execute(stmt)
                connection.commit()
                return result
        except Exception as e:
            connection.rollback()
            raise
        engine.dispose()

async def parse_and_save(sqlalchemy_url, session, url):
    engine = create_engine(sqlalchemy_url)
    
    metadata = MetaData()
    task_table = Table(
        'task', 
        metadata,
        autoload_with=engine
    )        
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()        
        soup = BeautifulSoup(html, 'html.parser')
        if url in [
            'https://www.leadertask.ru/blog/celi-na-etot-god',
            'https://www.makingsenseofcents.com/2022/12/goal-ideas.html',
            'https://facedragons.com/personal-development/list-of-goal-ideas/'
            ]:
            soup = soup.find_all('ul', {'class': 'wp-block-list'})
        else:
            soup = soup.find_all('ol')
        tasks = []
        for tag in soup:
            for task_index in tag.text.splitlines():
                if task_index != '':
                    tasks.append(task_index)
        await save(engine, task_table, tasks)
    
    except Exception as e:
        print(f"Error parsing {url}: {e}")

async def async_parser(sqlalchemy_url, urls):
    start_time = time.time()
    
    connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [parse_and_save(sqlalchemy_url, session, url) for url in urls]
        await asyncio.gather(*tasks)
    
    elapsed_time = time.time() - start_time
    return "Завершено"

def run_async_parser(sqlalchemy_url, sample_urls):
    asyncio.run(async_parser(sqlalchemy_url, sample_urls))
