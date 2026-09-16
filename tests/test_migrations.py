import pytest
from alembic.command import check
from alembic.config import Config

def test_no_uncommitted_migration_drift():
    """
    Fails if SQLAlchemy models have pending changes not recorded in Alembic migrations.
    """
    alembic_cfg = Config("alembic.ini")
    
    try:
        check(alembic_cfg)
    except Exception as e:
        pytest.fail(f"Alembic migration drift detected! Run 'alembic revision --autogenerate': {e}")
