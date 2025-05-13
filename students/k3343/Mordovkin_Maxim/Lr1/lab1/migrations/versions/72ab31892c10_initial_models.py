"""Initial models

Revision ID: 72ab31892c10
Revises: 9f561feff330
Create Date: 2025-04-28 23:34:52.641779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72ab31892c10'
down_revision: Union[str, None] = '9f561feff330'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
