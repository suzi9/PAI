from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.db import Base

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

sync_url = settings.DATABASE_URL.replace("asyncpg", "")

target_metadata = Base.metadata

def run_migrations_offline():
    url = sync_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )
    connection = connectable.connect()
    context.configure(connection=connection, target_metadata=target_metadata)
    context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
