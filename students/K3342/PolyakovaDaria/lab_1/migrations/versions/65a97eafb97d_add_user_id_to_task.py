"""Add user_id to task

Revision ID: 65a97eafb97d
Revises: d7bb2f7f0785
Create Date: 2025-04-28 15:29:30.443077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '65a97eafb97d'
down_revision: Union[str, None] = 'd7bb2f7f0785'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('task', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_task_user_id_user', 'task', 'user', ['user_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_task_user_id_user', 'task', type_='foreignkey')
    op.drop_column('task', 'user_id')

