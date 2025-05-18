from sqlalchemy import event
from app.models.models import Offer, SwapRequest, SwapStatus

def handle_offer_deletion(mapper, connection, target: Offer):
    """
    Вызывается перед удалением `Offer`.
    Обновляет `SwapRequest`, где `get_offer_id = target.id`:
    - `get_offer_id` → NULL
    - `status` → `OUTDATED`
    """
    print("Offer is being deleted!")

    connection.execute(
        SwapRequest.__table__.update()
        .where(SwapRequest.get_offer_id == target.id)
        .values(get_offer_id=None, status=SwapStatus.outdated)
    )

    print(f"SwapRequests updated for get_offer_id={target.id}")

    connection.execute(
        SwapRequest.__table__.delete()
        .where(SwapRequest.give_offer_id == target.id)
    )
    print(f"SwapRequests deleted where give_offer_id={target.id}")

def handle_offer_closure(mapper, connection, target: Offer):
    """
    Вызывается перед обновлением `Offer.is_open`.
    Обновляет `SwapRequest`, у которых `get_offer_id = target.id`,
    если `is_open` изменяется с `True` → `False`.
    """
    print("TRIGGERED: Offer is being updated!")

    if not target.is_open:
        print("OFFER IS CLOSING, UPDATING SwapRequest...")
        connection.execute(
            SwapRequest.__table__.update()
            .where((SwapRequest.get_offer_id == target.id) & (SwapRequest.status != SwapStatus.COMPLETED))
            .values(get_offer_id=None, status=SwapStatus.outdated)
        )
        print(f"✅ SwapRequests updated for get_offer_id={target.id}")

event.listen(Offer, "before_update", handle_offer_closure)
event.listen(Offer, "before_delete", handle_offer_deletion)
