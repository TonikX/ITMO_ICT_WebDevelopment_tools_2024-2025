В приложние, созданное в лабораторной работе 2 была добавлена ещё одна конечная точка

api.py:
```python
@app_router.post("/parse", tags=["Парсер"])
async def parse(url: str, server: Annotated[Monolite, Depends(get_monolite_server)]):
    return await server.parse(url, celery = False)
```

services.py:
```python
async def parse(self, url: str, celery: bool):
    if not celery:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(f"http://parser:8000/parse?url={url}") as response:
                return await response.json()
```

### Вывод
Было проработано создание конечной точки, обращающийся к другому url