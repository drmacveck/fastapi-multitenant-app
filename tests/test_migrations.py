import os
import asyncio
import pytest
from alembic.config import Config
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import text
from database import Base, engine

@pytest.mark.asyncio
async def test_no_uncommitted_migration_drift():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))

    # Execute DDL statements individually to satisfy asyncpg prepared statement constraints
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))

    # Run Alembic upgrade in thread worker
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

    # Compare DB state against Base.metadata
    async with engine.connect() as connection:
        def do_compare(sync_conn):
            context = MigrationContext.configure(sync_conn)
            return compare_metadata(context, Base.metadata)

        diff = await connection.run_sync(do_compare)

    assert diff == [], f"Alembic migration drift detected! New upgrade operations detected: {diff}"
