"""Add hashed_password column to user table

Revision ID: add_hashed_password
Revises: initial_schema
Create Date: 2025-05-14 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'add_hashed_password'
down_revision: Union[str, None] = 'initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add hashed_password column to user table."""
    op.add_column('user', sa.Column('hashed_password', sa.String(), nullable=True))
    
    # Set a default value for existing rows
    op.execute("UPDATE \"user\" SET hashed_password = 'changeme'")
    
    # Make the column non-nullable after setting default values
    op.alter_column('user', 'hashed_password', nullable=False)


def downgrade() -> None:
    """Remove hashed_password column from user table."""
    op.drop_column('user', 'hashed_password')