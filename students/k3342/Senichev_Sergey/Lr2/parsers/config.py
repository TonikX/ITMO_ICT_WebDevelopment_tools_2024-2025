import os
from typing import List
from pathlib import Path

# GitHub API Configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Optional, but recommended for higher rate limits

# List of repositories to parse issues from
REPOSITORIES: List[str] = [
    "python/cpython",
    "django/django",
    # "pallets/flask",
    # "psf/requests",
    # "pytest-dev/pytest"
]

# Maximum number of tasks to parse per repository
MAX_TASKS_PER_REPO = 10  # Set to None to parse all tasks

# Database Configuration
DB_PATH = Path(__file__).parent / "tasks.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Number of workers for parallel processing
THREAD_POOL_SIZE = 4
PROCESS_POOL_SIZE = 4
ASYNC_CONCURRENT_REQUESTS = 4

# Number of workers for parallel processing
NUM_WORKERS = 5 