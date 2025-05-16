import os, sys
from logging.config import fileConfig
from dotenv import load_dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

# ────────────────────────────────────────────────────────────────────────────
# 1) Абсолютный путь до папки practice:
current_dir = os.path.dirname(os.path.realpath(__file__))
practice_dir = os.path.abspath(
    os.path.join(
        current_dir,
        os.pardir,   # ↑ migrations → pr1.3
        os.pardir    # ↑ pr1.3 → practice
    )
)
# 2) Путь к .env внутри practice
dotenv_path = os.path.join(practice_dir, ".env")
print(f"→ Loading .env from {dotenv_path}")

# 3) Загружаем .env
load_dotenv(dotenv_path)

# 4) Проверяем, что переменная действительно подхватилась
db_url = os.getenv("DB_ADMIN")
if not isinstance(db_url, str):
    raise RuntimeError(f"Не удалось загрузить DB_ADMIN из {dotenv_path}, got {db_url!r}")

# 5) Подменяем URL в конфиге Alembic
config = context.config
config.set_main_option("sqlalchemy.url", db_url)
fileConfig(config.config_file_name)

# 6) Импорт моделей из вашего приложения
sys.path.insert(0, practice_dir)          # чтобы Python видел pr2 и другие пакеты
from pr2.models import *                  # или ваш пакет, где лежит models.py
target_metadata = SQLModel.metadata
# ────────────────────────────────────────────────────────────────────────────

# ... остальной код run_migrations_offline/online без изменений ...

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
