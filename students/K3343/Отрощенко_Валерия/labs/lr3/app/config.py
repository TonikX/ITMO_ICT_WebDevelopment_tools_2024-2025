import os
from dotenv import load_dotenv

load_dotenv()

DB_DSN = os.getenv("DB_ADMIN", "postgresql://postgres:postgres@localhost:1928/hackathons_db")
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))

PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8000")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

DEFAULT_URLS = [
    u.strip() for u in os.getenv(
        "DEFAULT_URLS",
        "https://hackathons.pro/tpost/jmg3d12jj1-hakaton-vkrum-ot-rtu-mirea-vk-i-rustore,"
        "https://hackathons.pro/tpost/220m4u3631-hakaton-po-prompt-inzhiniringu-ekспrompt,"
        "https://hackathons.pro/tpost/7i620ksj51-vserossiiskii-hakaton-fits-2024"
    ).split(",") if u.strip()
]