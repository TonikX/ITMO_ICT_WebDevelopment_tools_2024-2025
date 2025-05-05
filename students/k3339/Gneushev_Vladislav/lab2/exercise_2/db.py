import os
import random
import asyncpg
import psycopg2
from psycopg2 import extras

SYNC_DSN = os.getenv("SYNC_DSN")
ASYNC_DSN = os.getenv("ASYNC_DSN")

MIN_CAPACITY = 10
MAX_CAPACITY = 100

def get_random_capacity():
    return random.randint(MIN_CAPACITY, MAX_CAPACITY)


def sync_save_bus(names: list[str]):
    data_to_insert = [(name, get_random_capacity()) for name in names]
    if not data_to_insert:
        return
    
    with psycopg2.connect(SYNC_DSN) as conn:
        with conn.cursor() as cur:
            extras.execute_values(
                cur,
                "INSERT INTO bus_types (name, people_capacity) VALUES %s",
                data_to_insert
            )
            conn.commit()


async def async_save_bus(names: list[str], pool: asyncpg.Pool):
    data_to_insert = [(name, get_random_capacity()) for name in names]
    if not data_to_insert:
        return
        
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(
                "INSERT INTO bus_types (name, people_capacity) VALUES ($1, $2)", 
                data_to_insert
            )

