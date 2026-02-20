from __future__ import with_statement

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from dotenv import load_dotenv

# Damit "src.*" importierbar ist:
BASE_DIR = Path(__file__).resolve().parents[1]  # backend/
sys.path.insert(0, str(BASE_DIR))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# .env laden (backend/.env)
load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL nicht gesetzt. Bitte in backend/.env eintragen.")

# Alembic-Config URL überschreiben
config.set_main_option("sqlalchemy.url", db_url)

from src.app.db.base import Base  # noqa: E402
from src.app import models  # noqa: F401, E402

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    engine = create_engine(db_url, poolclass=pool.NullPool, connect_args=connect_args)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()