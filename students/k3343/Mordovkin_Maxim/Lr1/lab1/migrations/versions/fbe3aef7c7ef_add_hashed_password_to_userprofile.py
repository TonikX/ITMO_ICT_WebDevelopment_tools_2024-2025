"""add hashed_password to userprofile

Revision ID: fbe3aef7c7ef
Revises: af38a0a232e4
Create Date: 2025-04-29 21:11:45.401874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fbe3aef7c7ef'
down_revision: Union[str, None] = 'af38a0a232e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
