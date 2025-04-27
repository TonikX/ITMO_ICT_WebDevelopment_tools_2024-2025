from task2.common.connection import get_session
from task2.common.models import Hackathon


def save_hackathon(data):
    with next(get_session()) as session:
        hackathon = Hackathon(
            name=data["name"],
            description=data["description"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            organizer_id=1
        )
        session.add(hackathon)
        session.commit()
