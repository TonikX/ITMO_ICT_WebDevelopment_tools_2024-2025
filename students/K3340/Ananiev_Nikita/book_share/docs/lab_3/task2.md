## **Подзадача 2**: Вызов парсера из FastAPI
### Интегрируем функциональность парсера в наше основное приложение

Так выглядит вызов парсера из fastapi:
```python
@celery_app.task(name="parser_task")
def parser_task():
    response = requests.post(os.getenv("PARSER_URL"))
    return response.json()


@book_router.post("/parse_books", response_model=TaskCreated)
@auth_checker
async def parse_books(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    task = parser_task.delay()
    response = TaskCreated(task_id=task.id)
    return response


@book_router.get("/parse_books/{task_id}")
@auth_checker
async def parse_books_result(task_id: str, credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    timeout = 10
    parsing = AsyncResult(task_id)
    for _ in range(timeout):
        if parsing.ready():
            return parsing.result
        await asyncio.sleep(1)
    raise HTTPException(status_code=408, detail="parsing timeout")
```

Здесь приведена реализация уже вместе с Celery, но можно и просто внутри эндпоинта, используя requests или aiohttp, отправлять запросы к контейнеру с парсером.