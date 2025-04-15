"""
Скрипт для применения миграций к базе данных
"""
import os
import sys
from subprocess import run

# Добавляем путь к проекту в sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Запускаем команду alembic для применения миграций
result = run(
    ["alembic", "upgrade", "head"], 
    cwd=os.path.abspath(os.path.dirname(__file__))
)

if result.returncode == 0:
    print("Миграции успешно применены")
else:
    print("Ошибка при применении миграций") 