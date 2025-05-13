"""Initial models

Revision ID: f8e3751047e8
Revises: 72ab31892c10
Create Date: 2025-04-29 21:00:44.553709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8e3751047e8'
down_revision: Union[str, None] = '72ab31892c10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
