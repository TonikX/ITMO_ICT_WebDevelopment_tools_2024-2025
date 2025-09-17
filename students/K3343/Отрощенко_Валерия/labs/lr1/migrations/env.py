import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────────────────────────────
# 1) Определяем корень проекта там, где лежат .env и models.py.
#    env.py находится в labs/lr1/migrations/env.py,
#    поэтому достаточно подняться на один уровень вверх — в labs/lr1:
current_dir = os.path.dirname(os.path.realpath(__file__))       # …/labs/lr1/migrations
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))  # …/labs/lr1

# 2) Добавляем его в sys.path, чтобы Python увидел ваш models.py
sys.path.insert(0, project_root)

# 3) Загружаем .env именно из labs/lr1
dotenv_path = os.path.join(project_root, ".env")
print(f"→ Loading .env from {dotenv_path}")
load_dotenv(dotenv_path)

# 4) Получаем URL из переменной окружения
db_url = os.getenv("DB_ADMIN")
if not isinstance(db_url, str):
    raise RuntimeError(f"Не найдена переменная DB_ADMIN в {dotenv_path!r}")

# 5) Подменяем placeholder из alembic.ini
config = context.config
config.set_main_option("sqlalchemy.url", db_url)

# 6) Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 7) Импортируем модели для автогенерации
from models import *   # noqa: F401,F403
target_metadata = SQLModel.metadata
# ────────────────────────────────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()