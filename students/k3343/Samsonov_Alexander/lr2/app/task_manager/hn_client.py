import asyncio
from random import random
from typing import List

import httpx

sem = asyncio.Semaphore(10)


async def get_item_by_id(item_id: int, client: httpx.AsyncClient):
    await asyncio.sleep(random()/10)
    async with sem:
        try:
            response = await client.get(f"/item/{item_id}.json")
            return response.json()
        except Exception as e:
            print(e)
            return None


async def parse_item_array(items: List[int], client: httpx.AsyncClient):
    tasks = [get_item_by_id(i, client) for i in items]

    return await asyncio.gather(*tasks)


async def traverse_item(item_id: int, client: httpx.AsyncClient, depth=0):
    node = await get_item_by_id(item_id, client)

    if depth == 0:
        return node

    kids = node.get('kids', [])
    tasks = [traverse_item(i, client, depth - 1) for i in kids]
    node['kids'] = await asyncio.gather(*tasks)

    return node

async def traverse_item_to_array(item_id: int, client: httpx.AsyncClient, depth=0):
    node = await get_item_by_id(item_id, client)
    items = [node]

    if depth == 0:
        return items

    kids = node.get('kids', [])
    tasks = [traverse_item_to_array(i, client, depth - 1) for i in kids]
    items.extend(sum(await asyncio.gather(*tasks, return_exceptions=False), []))

    return items

async def get_user_data(user_id: str, client: httpx.AsyncClient):
    response = await client.get(f"/user/{user_id}.json")
    return response.json()


async def traverse_user_data(user_id: str, client: httpx.AsyncClient):
    user = await get_user_data(user_id, client)

    submitions = user.get('submitted', [])

    user['submitted'] = await parse_item_array(submitions, client)
    return user


async def get_top_stories(client: httpx.AsyncClient) -> List[int]:
    response = await client.get("/topstories.json")
    response.raise_for_status()
    return response.json()


async def get_new_stories(client: httpx.AsyncClient) -> List[int]:
    response = await client.get("/newstories.json")
    response.raise_for_status()
    return response.json()


async def get_best_stories(client: httpx.AsyncClient) -> List[int]:
    response = await client.get("/beststories.json")
    response.raise_for_status()
    return response.json()
