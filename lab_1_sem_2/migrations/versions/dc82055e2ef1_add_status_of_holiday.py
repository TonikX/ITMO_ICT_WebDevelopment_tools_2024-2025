"""add status of holiday

Revision ID: dc82055e2ef1
Revises: 61c7ef6cc6d4
Create Date: 2025-05-03 17:04:08.886677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'dc82055e2ef1'
down_revision: Union[str, None] = '61c7ef6cc6d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE TYPE triprequeststatus AS ENUM ('pending', 'accepted', 'rejected', 'completed');
    """)

    op.execute("""
    ALTER TABLE triprequest 
    ALTER COLUMN status 
    TYPE triprequeststatus 
    USING status::triprequeststatus;
    """)


def downgrade() -> None:

    op.alter_column('triprequest', 'status',
               existing_type=sa.Enum('pending', 'accepted', 'rejected', 'completed', name='triprequeststatus'),
               type_=sa.VARCHAR(),
               existing_nullable=False,
               existing_server_default='pending')

    op.execute("DROP TYPE triprequeststatus;")


    # ### end Alembic commands ###
