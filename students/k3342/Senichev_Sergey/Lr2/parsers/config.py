import os
from typing import List
from pathlib import Path

# GitHub API Configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

REPOSITORIES: List[str] = [
    "python/cpython",
    "django/django",
    # "pallets/flask",
    # "psf/requests",
    # "pytest-dev/pytest"
]

MAX_TASKS_PER_REPO = 10

DB_PATH = Path(__file__).parent / "tasks.db"
DB_URL = f"sqlite:///{DB_PATH}"

THREAD_POOL_SIZE = 4
PROCESS_POOL_SIZE = 4
ASYNC_CONCURRENT_REQUESTS = 4

NUM_WORKERS = 5 