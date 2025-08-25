from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.db.base import Base

# IMPORTANT: importez vos modèles ici quand vous les créez, ex:
# from app.models import client, technician, intervention, event  # noqa: F401

config = context.config

# Source unique de vérité: settings.DATABASE_URL (.env)
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    kwargs = dict(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=_is_sqlite(url),  # nécessaire pour ALTER sous SQLite
    )
    context.configure(**kwargs)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    url = config.get_main_option("sqlalchemy.url")
    connectable = create_engine(url, poolclass=pool.NullPool, future=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=_is_sqlite(url),
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
