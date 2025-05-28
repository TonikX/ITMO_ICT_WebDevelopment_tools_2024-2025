"""create parsed_urls table

Revision ID: create_parsed_urls_table
Create Date: 2024-05-25 19:25:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('parsed_urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('parsed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('parsed_urls')