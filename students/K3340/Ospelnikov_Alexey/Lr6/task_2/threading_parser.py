import threading
import sqlite3
import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
import time


from sqlalchemy.sql import insert
from sqlalchemy import create_engine, MetaData, Table, select

import time

def save(engine, task_table, task_name):
    
    with engine.connect() as connection:
        try:
            stmt = insert(task_table).values(
                name=task_name,
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

def parse_and_save(sqlalchemy_url, url):
    engine = create_engine(sqlalchemy_url)
    metadata = MetaData()
    task_table = Table(
        'task', 
        metadata,
        autoload_with=engine
    )        
    resp = req.get(url)
 
    soup = BeautifulSoup(resp.text, 'html.parser')
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
    save(engine, task_table, tasks)  
                
    
def threading_parser(sqlalchemy_url, urls):
    start_time = time.time()
    num_threads = 6
    chunk_size = len(urls) // num_threads
    threads = []
    
    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size if i < num_threads - 1 else len(urls)
        thread_urls = urls[start:end]
        
        thread = threading.Thread(
            target=lambda urls: [parse_and_save(sqlalchemy_url, url) for url in urls],
            args=(thread_urls,),
            name=f"Thread-{i+1}"
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    elapsed_time = time.time() - start_time
    print(f"Threading: {elapsed_time:.2f} сек.")

def run_threading_parser(sqlalchemy_url, urls):
    threading_parser(sqlalchemy_url, urls)