"""hui

Revision ID: 768426f9c890
Revises: 9d4c59e6b7de
Create Date: 2025-04-29 21:17:38.121846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '768426f9c890'
down_revision: Union[str, None] = '9d4c59e6b7de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
