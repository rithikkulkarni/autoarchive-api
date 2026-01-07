import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.db.base import Base
from app.db import models  # noqa: F401

config = context.config

# Set up Python logging.
fileConfig(config.config_file_name)

# Tell Alembic what metadata to inspect
target_metadata = Base.metadata


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)

    # Use DATABASE_URL from .env / environment
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # detect column type changes
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()