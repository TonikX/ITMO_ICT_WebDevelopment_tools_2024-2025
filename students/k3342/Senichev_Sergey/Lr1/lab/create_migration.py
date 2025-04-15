import os
import sys
from subprocess import run

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

result = run(
    ["alembic", "revision", "--autogenerate", "-m", "Initial migration"], 
    cwd=os.path.abspath(os.path.dirname(__file__))
)

if result.returncode == 0:
    print("Миграция успешно создана")
else:
    print("Ошибка при создании миграции") 