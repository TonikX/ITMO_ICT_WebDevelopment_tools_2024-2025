from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
current_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(os.path.dirname(current_dir))
app_dir = os.path.join(project_dir, 'app')
sys.path.insert(0, project_dir)
sys.path.insert(0, app_dir)

from models import Base

config = context.config

# Override alembic.ini settings with environment variables
db_url = os.getenv('ALEMBIC_DB_URL')
if db_url:
    config.set_main_option('sqlalchemy.url', db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

def get_engine():
    """Create SQLAlchemy engine with environment variables"""
    return create_engine(
        os.getenv('ALEMBIC_DB_URL'),
        connect_args={"client_encoding": "utf8"}
    )

# Rest of the file remains unchanged
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    engine = get_engine()
    url = str(engine.url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create engine directly
    connectable = get_engine()

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