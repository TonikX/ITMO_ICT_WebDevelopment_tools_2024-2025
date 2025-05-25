"""create parsed_urls table

Revision ID: 001
Create Date: 2024-03-19 19:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('parsed_urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('parsed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.String(length=50), server_default='completed'),
        sa.Column('task_id', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parsed_urls_url'), 'parsed_urls', ['url'])

def downgrade() -> None:
    op.drop_index(op.f('ix_parsed_urls_url'), table_name='parsed_urls')
    op.drop_table('parsed_urls')