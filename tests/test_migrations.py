import os
import asyncio
import pytest
from alembic.config import Config
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from database import Base, engine

@pytest.mark.asyncio
async def test_no_uncommitted_migration_drift():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))

    # Drop application tables specifically without touching alembic_version
    async with engine.begin() as conn:
        def drop_app_tables(sync_conn):
            for table in reversed(Base.metadata.sorted_tables):
                table.drop(sync_conn, checkfirst=True)
        await conn.run_sync(drop_app_tables)

    # Apply Alembic migrations from scratch on a clean DB
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    # Compare applied schema against Base.metadata
    async with engine.connect() as connection:
        def do_compare(sync_conn):
            context = MigrationContext.configure(sync_conn)
            return compare_metadata(context, Base.metadata)

        diff = await connection.run_sync(do_compare)

    assert diff == [], f"Alembic migration drift detected! New upgrade operations detected: {diff}"
