import os
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

    async with engine.begin() as conn:
        def run_migration_check(sync_conn):
            # Drop existing tables to guarantee a clean schema test
            Base.metadata.drop_all(sync_conn)

            # Bind the sync connection to Alembic config
            alembic_cfg.attributes["connection"] = sync_conn
            command.upgrade(alembic_cfg, "head")

            # Perform drift comparison on the same active connection
            context = MigrationContext.configure(sync_conn)
            return compare_metadata(context, Base.metadata)

        diff = await conn.run_sync(run_migration_check)

    assert diff == [], f"Alembic migration drift detected! New upgrade operations detected: {diff}"
