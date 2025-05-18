import os
import re
import random
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URI = os.environ["DB_URL"]

def get_connection():
    return psycopg2.connect(DATABASE_URI)

def create_user_record(full_name: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Проверяем, есть ли уже такой full_name
            cursor.execute('SELECT 1 FROM "user" WHERE full_name = %s', (full_name,))
            if cursor.fetchone():
                return

            username = re.sub(r"[^a-zA-Z0-9]", "", full_name.lower())[:30] + str(random.randint(1000, 9999))
            email = f"{username}@example.com"
            password = "default_hashed"
            phone = f"+7900{random.randint(1000000, 9999999)}"
            joined_at = datetime.utcnow()

            cursor.execute(
                """
                INSERT INTO "user" (username, email, password, full_name, phone_number, profile_image, joined_at, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (username, email, password, full_name, phone, None, joined_at, 'user')  # 'user' для RoleType.user
            )
        conn.commit()
    except Exception as e:
        print(f"DB error on inserting {full_name}: {e}")
    finally:
        conn.close()
