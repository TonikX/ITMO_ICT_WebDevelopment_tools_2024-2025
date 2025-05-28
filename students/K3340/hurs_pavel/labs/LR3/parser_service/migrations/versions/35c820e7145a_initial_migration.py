"""Initial migration

Revision ID: 35c820e7145a
Revises: 
Create Date: 2025-05-25 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '35c820e7145a'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('parsed_urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('parsed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('parsed_urls') 