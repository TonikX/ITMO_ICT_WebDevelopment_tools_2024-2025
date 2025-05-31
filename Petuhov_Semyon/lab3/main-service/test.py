from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DB_ADMIN")
print(repr(db_url))  # ПОКАЖЕТ ВСЕ СКРЫТЫЕ СИМВОЛЫ
print(os.getenv('SECRET_KEY'))
print(os.getenv('ALGORITHM'))