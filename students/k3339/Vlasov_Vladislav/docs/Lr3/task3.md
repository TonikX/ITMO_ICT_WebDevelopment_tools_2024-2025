Сначала были установлены брокер сообщений и очереди задач

Затем наcтроенна задача и создан соответствующий эндпоинт в приложении парсера:

```python
celery = Celery('tasks', broker='redis://redis:6379', backend='redis://redis:6379')


@celery.task
def parse_celery(url: str):
    return asyncio.run(parse(url))
```

```python
@app.post("/parse/celery")
async def start_parse_celery(url: str):
    task = parse_celery.delay(url)
    return {"task_id": task.id}
```

Обновлён docker-compose.yml
```
  redis:
    image: redis
    ports:
      - "6379:6379"
    container_name: redis

  celery_worker:
    build:
      context: ./parser
      dockerfile: DockerFile
    command: celery -A tasks.celery worker --pool=solo
    env_file: .env
    depends_on:
      - redis
```

И добавлена новая конечная точка в главное приложение
```python
@app_router.post("/parse/celery", tags=["Парсер"])
async def parse_celery(url: str, server: Annotated[Monolite, Depends(get_monolite_server)]):
    return await server.parse(url, celery = True)
```

```python
    async def parse(self, url: str, celery: bool):
        if not celery:
            async with aiohttp.ClientSession() as http_session:
                async with http_session.post(f"http://parser:8000/parse?url={url}") as response:
                    return await response.json()
        
        else:
            async with aiohttp.ClientSession() as http_session:
                async with http_session.post(f"http://parser:8000/parse/celery?url={url}") as response:
                    return await response.json()
```

### Вывод

Изучены очерели сообщений, их работа с брокером и способ настройки их в Docker