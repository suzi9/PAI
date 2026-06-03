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
        literal_binds=False,  
    )
    context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy."
    )

    context.configure(connection=connectable)  
    context.run_migrations()  

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
