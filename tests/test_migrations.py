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

    def run_alembic_cycle():
        # Downgrade to base to cleanly drop tables & reset alembic_version
        try:
            command.downgrade(alembic_cfg, "base")
        except Exception:
            pass
        # Upgrade to head to apply all migrations fresh
        command.upgrade(alembic_cfg, "head")

    # Run Alembic operations in worker thread
    await asyncio.to_thread(run_alembic_cycle)

    # Compare applied database schema against Base.metadata
    async with engine.connect() as connection:
        def do_compare(sync_conn):
            context = MigrationContext.configure(sync_conn)
            return compare_metadata(context, Base.metadata)

        diff = await connection.run_sync(do_compare)

    assert diff == [], f"Alembic migration drift detected! New upgrade operations detected: {diff}"
