import os
import sys
from subprocess import run

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

result = run(
    ["alembic", "upgrade", "head"], 
    cwd=os.path.abspath(os.path.dirname(__file__))
)

if result.returncode == 0:
    print("Миграции успешно применены")
else:
    print("Ошибка при применении миграций") 