"""Add user model

Revision ID: d7bb2f7f0785
Revises: 
Create Date: 2025-04-02 15:36:54.208396
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd7bb2f7f0785'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Схема обновления"""
    op.add_column('user', sa.Column('role', postgresql.ENUM('user', 'admin', name='role'), nullable=False,
                                    server_default='user'))


def downgrade() -> None:
    """Схема понижения"""
    op.drop_column('user', 'role')
