from db.connection import get_session
from db.models import User


def save_users(user_list):
    with next(get_session()) as session:
        for user in user_list:
            new_user = User(
                name=user["name"],
                email=user["email"],
                password=user["password"],
                bio=user["bio"]
            )
            session.add(new_user)
        session.commit()


async def save_user_async(user_list):
    async for session in get_session():
        async with session.begin():
            for user in user_list:
                new_user = User(
                    name=user["name"],
                    email=user["email"],
                    password=user["password"],
                    bio=user["bio"]
                )
                session.add(new_user)
            await session.commit()