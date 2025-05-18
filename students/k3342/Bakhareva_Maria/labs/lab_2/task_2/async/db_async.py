import re
import random
from datetime import datetime
from students.k3342.Bakhareva_Maria.labs.lab_1.models.models import RoleType

async def create_user_record(conn, full_name: str) -> None:
    existing = await conn.fetchval('SELECT 1 FROM "user" WHERE full_name = $1', full_name)
    if existing:
        return

    username = re.sub(r"[^a-zA-Z0-9]", "", full_name.lower())[:30] + str(random.randint(1000, 9999))
    email = f"{username}@example.com"
    password = "default_hashed"
    phone = f"+7900{random.randint(1000000, 9999999)}"

    await conn.execute(
        """
        INSERT INTO "user" (username, email, password, full_name, phone_number, profile_image, joined_at, role)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        username,
        email,
        password,
        full_name,
        phone,
        None,
        datetime.utcnow(),
        RoleType.user,
    )
