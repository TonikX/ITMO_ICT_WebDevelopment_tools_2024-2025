"""add hashed_password to userprofile

Revision ID: 9d4c59e6b7de
Revises: fbe3aef7c7ef
Create Date: 2025-04-29 21:14:04.154824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d4c59e6b7de'
down_revision: Union[str, None] = 'fbe3aef7c7ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
