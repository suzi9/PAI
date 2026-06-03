from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config

from app.config import settings

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

sync_url = settings.DATABASE_URL

def run_migrations_offline():
    context.configure(
        url=sync_url,
        compare_type=True,   
    )
    context.run_migrations()

run_migrations_offline()
