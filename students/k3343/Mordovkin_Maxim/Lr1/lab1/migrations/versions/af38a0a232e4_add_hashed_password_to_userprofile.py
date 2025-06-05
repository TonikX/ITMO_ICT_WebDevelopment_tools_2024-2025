"""Add hashed_password to userprofile

Revision ID: af38a0a232e4
Revises: f8e3751047e8
Create Date: 2025-04-29 21:08:03.214427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af38a0a232e4'
down_revision: Union[str, None] = 'f8e3751047e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
