import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DB_URL")

config = context.config
config.set_main_option('sqlalchemy.url', db_url)

from sqlmodel import SQLModel
from models.user_model import User
from models.team_model import Team
from models.team_membership_model import TeamMembership
from models.hackathon_model import Hackathon
from models.task_model import Task
from models.submission_model import Submission

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
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
