"""
Скрипт для создания первой миграции
"""
import os
import sys
from subprocess import run

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Запускаем команду alembic для создания миграции
result = run(
    ["alembic", "revision", "--autogenerate", "-m", "Initial migration"], 
    cwd=os.path.abspath(os.path.dirname(__file__))
)

if result.returncode == 0:
    print("Миграция успешно создана")
else:
    print("Ошибка при создании миграции") 