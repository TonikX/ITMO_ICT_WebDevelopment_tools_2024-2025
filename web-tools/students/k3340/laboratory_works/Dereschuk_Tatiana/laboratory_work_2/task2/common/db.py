
from team_finder_lab2.task2.common.connection import get_session
from team_finder_lab2.task2.common.models import User


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
