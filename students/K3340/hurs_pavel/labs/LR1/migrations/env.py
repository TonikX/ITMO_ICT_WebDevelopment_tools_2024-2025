import os
from logging.config import fileConfig
from sqlmodel import SQLModel
from models.user_model import User
from models.task_model import Task
from models.time_entry_model import TimeEntry
from models.task_assignment_model import TaskAssignment
from sqlalchemy import engine_from_config, pool
from alembic import context

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
config = context.config
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise RuntimeError("Переменная окружения DATABASE_URL не установлена")
config.set_main_option('sqlalchemy.url', db_url)

fileConfig(config.config_file_name)


target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Запуск миграций в автономном режиме (без подключения к БД)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций в режиме онлайн (с подключением к БД)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
