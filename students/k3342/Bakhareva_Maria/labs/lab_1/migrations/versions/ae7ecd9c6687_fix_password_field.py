from typing import Sequence, Union
import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'ae7ecd9c6687'
down_revision: Union[str, None] = '2422babcd742'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем столбец password с nullable=True, чтобы избежать проблем с уже существующими строками
    op.add_column('user', sa.Column('password', sa.String(), nullable=True))

    # 2. Заполняем столбец password значением по умолчанию, чтобы не было NULL
    op.execute(
        text('UPDATE "user" SET password = :default_password WHERE password IS NULL')
        .params(default_password='default_password')
    )

    # 3. Теперь можем изменить столбец на NOT NULL
    op.alter_column('user', 'password', nullable=False)

    # 4. Удаляем старый столбец password_hash
    op.drop_column('user', 'password_hash')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Добавляем столбец password_hash
    op.add_column('user', sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False))

    # 2. Удаляем столбец password
    op.drop_column('user', 'password')
