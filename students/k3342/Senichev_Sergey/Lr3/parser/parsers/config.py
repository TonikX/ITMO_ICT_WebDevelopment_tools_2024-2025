import os
from typing import List

# GitHub API Configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

REPOSITORIES: List[str] = [
    "python/cpython",
    "django/django",
]

MAX_TASKS_PER_REPO = int(os.getenv("MAX_TASKS_PER_REPO", "10"))

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

THREAD_POOL_SIZE = int(os.getenv("THREAD_POOL_SIZE", "4"))
PROCESS_POOL_SIZE = int(os.getenv("PROCESS_POOL_SIZE", "4"))
ASYNC_CONCURRENT_REQUESTS = int(os.getenv("ASYNC_CONCURRENT_REQUESTS", "4"))

NUM_WORKERS = 5 