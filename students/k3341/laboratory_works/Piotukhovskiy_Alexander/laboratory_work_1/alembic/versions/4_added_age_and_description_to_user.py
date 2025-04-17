"""Added age and description to user

Revision ID: 4
Revises: 3
Create Date: 2025-04-03 21:47:49.567453

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4'
down_revision: Union[str, None] = '3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user', sa.Column('age', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('user', 'description')
    op.drop_column('user', 'age')
