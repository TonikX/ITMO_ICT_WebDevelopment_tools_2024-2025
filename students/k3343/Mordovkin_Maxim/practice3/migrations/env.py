import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from sqlmodel import SQLModel

# загружаем .env
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# импортируем все модели, чтобы SQLModel.metadata был полным
from app.models import *  

# Alembic Config object
config = context.config

# передаём строку из .env в Alembic
db_url = os.getenv("DB_ADMIN")
if not db_url:
    raise RuntimeError("Не задана переменная DB_ADMIN в .env")
config.set_main_option("sqlalchemy.url", db_url)

# настраиваем логирование
fileConfig(config.config_file_name)

# указываем метаданные наших моделей для autogenerate
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
