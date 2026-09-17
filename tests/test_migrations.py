import pytest
from alembic.config import Config
from alembic import command

def test_no_uncommitted_migration_drift():
    """
    Fails if SQLAlchemy models have pending changes not recorded in Alembic migrations.
    """
    alembic_cfg = Config("alembic.ini")

    try:
        # 1. Bring the test database up to the latest revision
        command.upgrade(alembic_cfg, "head")
        
        # 2. Check if models have uncommitted changes relative to migration scripts
        command.check(alembic_cfg)
    except Exception as e:
        pytest.fail(f"Alembic migration drift detected! Run 'alembic revision --autogenerate': {e}")
