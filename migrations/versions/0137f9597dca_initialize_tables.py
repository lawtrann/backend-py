"""initialize_tables

Revision ID: 0137f9597dca
Revises: 
Create Date: 2026-02-20 01:05:18.981184

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0137f9597dca'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
REVISION_MESSAGE: str = 'initialize_tables'

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def upgrade() -> None:
    """Upgrade schema."""
    sql = (SQL_DIR / "0137f9597dca_initialize_tables_upgrade.sql").read_text()
    op.execute(sql)


def downgrade() -> None:
    """Downgrade schema."""
    sql = (SQL_DIR / "0137f9597dca_initialize_tables_downgrade.sql").read_text()
    op.execute(sql)
