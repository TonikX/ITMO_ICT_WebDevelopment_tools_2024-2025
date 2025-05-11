"""Добавление скиллов в таблицу skill

Revision ID: 3
Revises: 2
Create Date: 2025-04-03 21:14:12.272007

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = '3'
down_revision: Union[str, None] = '2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    skills_data = [
        {
            "id": str(uuid.uuid4()),
            "name": "Организация путешествий",
            "description": "Умение планировать маршруты и организовывать поездки."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Коммуникация",
            "description": "Навыки общения с людьми разных культур и национальностей."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Адаптивность",
            "description": "Способность быстро адаптироваться к новым условиям и изменениям."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Навыки навигации",
            "description": "Умение ориентироваться на местности, пользоваться картами и GPS."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Управление бюджетом",
            "description": "Опыт планирования и контроля расходов во время путешествий."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Знание иностранных языков",
            "description": "Способность общаться на разных языках, что облегчает поездки."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Фотография",
            "description": "Навыки съемки интересных и запоминающихся кадров в путешествиях."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Лидерство",
            "description": "Умение вести группу и принимать решения в нестандартных ситуациях."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Приключенческий дух",
            "description": "Готовность к новым открытиям и нестандартным ситуациям в пути."
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Кулинарные навыки",
            "description": "Умение готовить национальные блюда и экспериментировать с местной кухней."
        }
    ]

    skill_table = sa.table(
        'skill',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True)
    )
    op.bulk_insert(skill_table, skills_data)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DELETE FROM skill
        WHERE name IN (
            'Организация путешествий',
            'Коммуникация',
            'Адаптивность',
            'Навыки навигации',
            'Управление бюджетом',
            'Знание иностранных языков',
            'Фотография',
            'Лидерство',
            'Приключенческий дух',
            'Кулинарные навыки'
        )
        """
    )
