import os
import sys

# 1) добавляем корень проекта (lab1/) в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from alembic import context
from dotenv import load_dotenv

# 2) подтягиваем .env и настраиваем URL
load_dotenv()
config = context.config
config.set_main_option("sqlalchemy.url", os.getenv("DB_ADMIN"))

# 3) логирование
if config.config_file_name:
    fileConfig(config.config_file_name)

# 4) импортируем модели из вашего пакета `app`
from app.models import UserProfile, Trip, TripParticipantLink  # noqa

target_metadata = SQLModel.metadata

# … дальше обычный код run_migrations_offline/online …
