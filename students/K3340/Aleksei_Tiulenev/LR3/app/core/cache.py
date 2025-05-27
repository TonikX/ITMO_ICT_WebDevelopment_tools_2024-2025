import os
import json
import redis
from typing import Optional, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_client = redis.from_url(REDIS_URL)

def set_cache(key: str, value: Any, expire: int = 3600):
    """Store value in cache"""
    redis_client.setex(key, expire, json.dumps(value))

def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None 