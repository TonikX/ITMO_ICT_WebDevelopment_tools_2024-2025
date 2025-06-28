from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
import time
import os

router = APIRouter()

# Конфигурация базы данных для парсера
PARSER_DB_CONFIG = {
    'host': os.getenv('PARSER_DB_HOST', 'localhost'),
    'database': os.getenv('PARSER_DB_NAME', 'web_parsing'),
    'user': os.getenv('PARSER_DB_USER', 'postgres'),
    'password': os.getenv('PARSER_DB_PASSWORD', 'postgres')
}

class ParseRequest(BaseModel):
    urls: List[str]
    method: str = "async"

class ParseResponse(BaseModel):
    success: bool
    message: str
    processed_urls: int
    execution_time: float

async def parse_and_save(session, db_pool, url):
    """Асинхронная функция для парсинга и сохранения данных"""
    try:
        start_time = time.perf_counter()

        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else 'No title'

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        async with db_pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO pages (url, title, execution_time, method) VALUES ($1, $2, $3, $4)',
                url, title, elapsed, "async"
            )

        print(f"Processed: {url} | Time: {elapsed:.2f}s | Method: async")
        return True

    except Exception as e:
        print(f"Failed to process {url}: {e}")
        return False

async def run_parser(urls: List[str]):
    """Запуск парсера в фоновом режиме"""
    try:
        db_pool = await asyncpg.create_pool(**PARSER_DB_CONFIG)
        
        async with aiohttp.ClientSession() as session:
            tasks = [parse_and_save(session, db_pool, url) for url in urls]
            results = await asyncio.gather(*tasks)
        
        await db_pool.close()
        
        successful = sum(results)
        print(f"Async parsing complete! Processed {successful}/{len(urls)} URLs")
        
    except Exception as e:
        print(f"Error in background parser: {e}")

@router.post("/parse", response_model=ParseResponse)
async def parse_urls(request: ParseRequest, background_tasks: BackgroundTasks):
    """
    Запускает парсинг указанных URL в фоновом режиме
    """
    if not request.urls:
        raise HTTPException(status_code=400, detail="URLs list cannot be empty")
    
    # Добавляем задачу в фоновые задачи
    background_tasks.add_task(run_parser, request.urls)
    
    return ParseResponse(
        success=True,
        message=f"Парсинг запущен для {len(request.urls)} URL(s)",
        processed_urls=len(request.urls),
        execution_time=0.0
    )

@router.get("/parse/status")
async def get_parse_status():
    """
    Получает статус последних операций парсинга
    """
    try:
        db_pool = await asyncpg.create_pool(**PARSER_DB_CONFIG)
        
        async with db_pool.acquire() as conn:
            # Получаем последние 10 записей
            rows = await conn.fetch(
                'SELECT url, title, execution_time, method, created_at FROM pages ORDER BY created_at DESC LIMIT 10'
            )
        
        await db_pool.close()
        
        results = []
        for row in rows:
            results.append({
                "url": row['url'],
                "title": row['title'],
                "execution_time": row['execution_time'],
                "method": row['method'],
                "created_at": row['created_at'].isoformat() if row['created_at'] else None
            })
        
        return {
            "success": True,
            "recent_parses": results,
            "total_count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting parse status: {str(e)}")

@router.get("/parse/test")
async def test_parse():
    """
    Тестовый эндпоинт для проверки работы парсера
    """
    test_urls = [
        'https://my.itmo.ru',
        'https://www.github.com',
        'https://www.stackoverflow.com'
    ]
    
    background_tasks = BackgroundTasks()
    background_tasks.add_task(run_parser, test_urls)
    
    return {
        "success": True,
        "message": "Тестовый парсинг запущен",
        "urls": test_urls
    } 