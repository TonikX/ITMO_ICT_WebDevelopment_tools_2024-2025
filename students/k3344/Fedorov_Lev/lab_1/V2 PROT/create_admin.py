import asyncio
import sys
import os
from passlib.context import CryptContext
import asyncpg

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import directly from app's models
from app.models import Base, User, Role, UsersRoles
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Local password hashing function
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


async def create_first_admin(username, email, password):
    # Hardcode database connection
    database_url = "postgresql+asyncpg://postgres:gucciskrrrt@localhost/hockey_db"

    # Create engine
    engine = create_async_engine(
        database_url,
        echo=True,
        pool_pre_ping=True,
    )

    # Create all tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        # Check if user exists
        result = await session.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User '{username}' already exists")
            return

        # Create new admin user
        new_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            status="active"
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        # Get or create admin role
        result = await session.execute(select(Role).where(Role.role_name == "admin"))
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            admin_role = Role(role_name="admin")
            session.add(admin_role)
            await session.commit()
            await session.refresh(admin_role)

        # Assign admin role to user
        user_role = UsersRoles(
            user_id=new_user.user_id,
            role_id=admin_role.role_id
        )
        session.add(user_role)
        await session.commit()

        print(f"Admin user '{username}' created successfully with ID: {new_user.user_id}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)

    asyncio.run(create_first_admin(sys.argv[1], sys.argv[2], sys.argv[3]))
