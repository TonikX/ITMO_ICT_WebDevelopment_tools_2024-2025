"""Merge branches

Revision ID: 69c30e808464
Revises: c83f6a63d63f, add_hashed_password
Create Date: 2025-05-14 13:17:25.014414

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69c30e808464'
down_revision: Union[str, None] = ('c83f6a63d63f', 'add_hashed_password')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
