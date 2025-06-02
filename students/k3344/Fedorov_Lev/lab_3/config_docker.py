import os
from pathlib import Path
from pydantic import BaseSettings


class DockerSettings(BaseSettings):
    """Настройки специфичные для Docker"""

    # Docker networking
    CONTAINER_NAME: str = "hockey_fastapi"
    PARSER_SERVICE_URL: str = "http://parser:8001"
    REDIS_SERVICE_URL: str = "redis://redis:6379"

    # Health check settings
    HEALTH_CHECK_TIMEOUT: int = 30
    SERVICE_STARTUP_TIMEOUT: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # File paths in container
    UPLOAD_DIR: Path = Path("/app/uploads")
    STATIC_DIR: Path = Path("/app/static")

    # Database settings for Docker
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Celery settings
    CELERY_TASK_TIMEOUT: int = 300  # 5 минут
    CELERY_WORKER_CONCURRENCY: int = 2

    class Config:
        env_file = ".env"
        case_sensitive = True


# Создаем экземпляр настроек
docker_settings = DockerSettings()

# Обновляем пути для uploads
PLAYER_PHOTOS_DIR = docker_settings.UPLOAD_DIR / "player_photos"
PLAYER_CERTIFICATES_DIR = docker_settings.UPLOAD_DIR / "player_certificates"
TEAM_LOGOS_DIR = docker_settings.UPLOAD_DIR / "team_logos"

# Создаем директории если их нет
for directory in [PLAYER_PHOTOS_DIR, PLAYER_CERTIFICATES_DIR, TEAM_LOGOS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


# Функция для проверки готовности сервисов
async def wait_for_service(url: str, timeout: int = 30) -> bool:
    """
    Ожидает готовности внешнего сервиса
    """
    import httpx
    import asyncio

    start_time = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start_time) < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                if response.status_code == 200:
                    return True
        except Exception:
            pass

        await asyncio.sleep(1)

    return False


# Настройки логирования для Docker
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": docker_settings.LOG_FORMAT,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": docker_settings.LOG_LEVEL,
        "handlers": ["default"],
    },
}
