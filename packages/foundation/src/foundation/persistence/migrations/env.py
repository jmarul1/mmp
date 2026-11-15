from alembic import context
from foundation.persistence.models import Base
from foundation.persistence.store import default_db_path
from sqlalchemy import create_engine

config = context.config


def database_url() -> str:
    return config.get_main_option("sqlalchemy.url") or f"sqlite:///{default_db_path()}"


def run_migrations() -> None:
    engine = create_engine(database_url())
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


run_migrations()
