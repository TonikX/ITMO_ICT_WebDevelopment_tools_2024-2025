from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Role, User, Season, UsersRoles
from .routes.users.user_security import get_password_hash
import asyncio


async def init_default_data(session: AsyncSession):
    """Создает начальные данные: роли, админа, сезон"""

    try:
        # 1. Создаем роли
        admin_role = await session.execute(select(Role).where(Role.role_name == "admin"))
        if not admin_role.scalar_one_or_none():
            admin_role_obj = Role(role_name="admin")
            session.add(admin_role_obj)

        user_role = await session.execute(select(Role).where(Role.role_name == "user"))
        if not user_role.scalar_one_or_none():
            user_role_obj = Role(role_name="user")
            session.add(user_role_obj)

        await session.commit()

        # 2. Создаем администратора
        admin_user = await session.execute(select(User).where(User.username == "admin"))
        if not admin_user.scalar_one_or_none():
            admin_user_obj = User(
                username="admin",
                email="admin@hockey.com",
                password_hash=get_password_hash("admin123"),
                name="Admin",
                surname="User",
                status="active"
            )
            session.add(admin_user_obj)
            await session.commit()
            await session.refresh(admin_user_obj)

            # 3. Назначаем роль админа
            admin_role_obj = await session.execute(select(Role).where(Role.role_name == "admin"))
            admin_role_obj = admin_role_obj.scalar_one()

            user_role_link = UsersRoles(
                user_id=admin_user_obj.user_id,
                role_id=admin_role_obj.role_id
            )
            session.add(user_role_link)

        # 4. Создаем базовый сезон
        season = await session.execute(select(Season).where(Season.year == "2024/2025"))
        if not season.scalar_one_or_none():
            season_obj = Season(year="2024/2025")
            session.add(season_obj)

        await session.commit()
        print("✅ Начальные данные созданы успешно")

    except Exception as e:
        print(f"❌ Ошибка создания начальных данных: {e}")
        await session.rollback()
        raise