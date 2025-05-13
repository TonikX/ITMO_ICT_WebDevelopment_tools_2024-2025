import asyncio
import os
import asyncpg
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

load_dotenv()
DB_ADMIN = os.getenv("DB_ADMIN")

# --------------------------------------------------
#  Pydantic-модель для тела запроса
# --------------------------------------------------
class ParseRequest(BaseModel):
    url: HttpUrl

# --------------------------------------------------
#  Инициализация FastAPI
# --------------------------------------------------
app = FastAPI(
    title="Async Parser Service",
    version="1.0",
    description="Асинхронный сервис-парсер: получает URL, скачивает страницу, разбирает title и сохраняет в БД"
)

# семафор для ограничения одновременных запросов внутри одного HTTP-вызова,
# на случай, если позже понадобится распараллелить batch-парсинг
MAX_CONCURRENT_FETCHES = 10
fetch_semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)


# --------------------------------------------------
#  Событие запуска: создаём пул соединений к PostgreSQL
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():
    try:
        app.state.db_pool = await asyncpg.create_pool(
            dsn=DB_ADMIN,
            min_size=1,
            max_size=MAX_CONCURRENT_FETCHES
        )
        print("Подключение к БД установлено (asyncpg pool).")
    except Exception as e:
        print(f" Не удалось создать пул соединений: {e}")
        raise


# --------------------------------------------------
#  Событие завершения: закрываем пул соединений
# --------------------------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    pool: asyncpg.Pool = app.state.db_pool  # type: ignore
    await pool.close()
    print("Пул соединений PostgreSQL закрыт.")


# --------------------------------------------------
#  Вспомогательная асинхронная функция для парсинга одного URL
# --------------------------------------------------
async def fetch_and_store_title(url: str, pool: asyncpg.Pool) -> str:
    """
    Асинхронно загружает URL (aiohttp), извлекает <title>, сохраняет в таблицу pages(url, title).
    Возвращает строку с найденным title.
    """
    async with fetch_semaphore:
        # 1) Асинхронно загружаем HTML через aiohttp
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    html = await resp.text()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=502, detail=f"Ошибка при загрузке {url}: {e}")

        # 2) Парсим HTML через BeautifulSoup (синхронная операция, но не слишком тяжёлая)
        soup = BeautifulSoup(html, "html.parser")
        raw_title = soup.title.string if soup.title and soup.title.string else ""
        title = raw_title.strip()

        # 3) Сохраняем в БД
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO page (url, title) VALUES ($1, $2)",
                    url,
                    title
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при сохранении в БД: {e}")

        return title


# --------------------------------------------------
#  Эндпоинт POST /parse: принимает JSON { "url": "..." }
# --------------------------------------------------
@app.post("/parse")
async def parse_endpoint(req: ParseRequest):
    """
    Получает на вход JSON с полем "url", асинхронно запрашивает страницу,
    извлекает <title> и сохраняет в таблицу pages.
    """
    url = req.url

    pool: asyncpg.Pool = app.state.db_pool  # type: ignore

    try:
        title = await fetch_and_store_title(str(url), pool)
    except HTTPException as e:
        # пробрасываем дальше HTTP-ошибки
        raise e
    except Exception as e:
        # непредвиденная внутренняя ошибка
        raise HTTPException(status_code=500, detail=f"Неизвестная ошибка при обработке: {e}")

    return {
        "message": "Parsing completed",
        "url": url,
        "title": title
    }
