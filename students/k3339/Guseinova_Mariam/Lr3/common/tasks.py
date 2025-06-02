from common.celery_app import app
import httpx
import os
import asyncio

# Получаем адрес парсера из переменных окружения
PARSER_SERVICE_URL = f"http://{os.getenv('PARSER_HOST', 'parser')}:{os.getenv('PARSER_PORT', '8001')}"


@app.task(bind=True, name='parser.parse_urls')
def parse_urls_task(self, urls: list[str], parser_type: str):
    """
    Задача Celery для асинхронного запуска парсинга.
    Вызывает HTTP-эндпоинт парсера.
    """
    try:
        # Для вызова асинхронной HTTP-функции используем asyncio.run
        async def _call_parser():
            async with httpx.AsyncClient() as client:
                print(f"[{self.request.id}] Sending parse request to {PARSER_SERVICE_URL}/parse for {len(urls)} URLs (type: {parser_type})...")
                response = await client.post(
                    f"{PARSER_SERVICE_URL}/parse",
                    json={"urls": urls, "parser_type": parser_type},
                    timeout=600
                )
                response.raise_for_status()
                print(f"[{self.request.id}] Parser service responded with: {response.json()}")
                return response.json()

        # Выполняем асинхронную функцию в синхронном контексте Celery
        result = asyncio.run(_call_parser())
        return result

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP Error triggering parser service (task {self.request.id}): {e.response.status_code} - {e.response.text}"
        print(error_msg)
        raise self.retry(exc=e, countdown=5, max_retries=3) # Повторяем задачу при HTTP ошибке
    except httpx.RequestError as e:
        error_msg = f"Network Error triggering parser service (task {self.request.id}): {str(e)}"
        print(error_msg)
        raise self.retry(exc=e, countdown=10, max_retries=5) # Повторяем задачу при сетевой ошибке
    except Exception as e:
        error_msg = f"Unexpected Error in parse_urls_task (task {self.request.id}): {str(e)}"
        print(error_msg)
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise