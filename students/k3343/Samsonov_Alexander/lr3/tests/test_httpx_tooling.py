import json
from pathlib import Path


import pytest
import respx
from httpx import Response

from app.task_manager.hn_client import get_item_by_id, traverse_item
from app.task_manager.utils import get_http_client

base_path = Path(__file__).parent


@pytest.mark.asyncio
@respx.mock
async def test_get_item_by_id():
    fake_data = {"id": 123, "title": "Test post"}
    route = respx.get("https://hacker-news.firebaseio.com/v0/item/123.json").mock(
        return_value=Response(200, json=fake_data)
    )

    async with get_http_client() as client:
        item = await get_item_by_id(123, client)

    assert route.called
    assert item["id"] == 123
    assert item["title"] == "Test post"


@pytest.mark.asyncio
@respx.mock
async def test_traverse_item_fake():
    respx.get("https://hacker-news.firebaseio.com/v0/item/1.json").mock(
        return_value=Response(200, json={"id": 1, "kids": [2, 3]})
    )
    respx.get("https://hacker-news.firebaseio.com/v0/item/2.json").mock(
        return_value=Response(200, json={"id": 2})
    )
    respx.get("https://hacker-news.firebaseio.com/v0/item/3.json").mock(
        return_value=Response(200, json={"id": 3})
    )

    async with get_http_client() as client:
        result = await traverse_item(1, client, depth=1)

    assert result["id"] == 1
    assert len(result["kids"]) == 2


@pytest.mark.asyncio
@respx.mock
async def test_traverse_item_real():
    root = 43669185

    with open(base_path / 'httpx_mock_data.json', 'r') as f:
        data = json.load(f)

    routes = [respx.get(f'https://hacker-news.firebaseio.com/v0/item/{i}.json').mock(
        return_value=Response(200, json=val)
    ) for i, val in data.items()]

    async with get_http_client() as client:
        result = await traverse_item(root, client, depth=1)
        assert result["id"] == root

    assert all(route.called for route in routes)
