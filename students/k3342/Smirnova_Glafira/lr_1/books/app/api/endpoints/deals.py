from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.endpoints.swaps_from import map_swap_in_list
from app.db.session import get_session
from app.api.dependencies.auth import get_current_user
from app.services.deal_service import get_user_deals
from app.schemas.deal import DealRead
from app.utils.time import format_datetime

router = APIRouter()

@router.get("/", response_model=list[DealRead])
def get_deal_history(
    user_id: int = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> list[DealRead]:
    """Возвращает историю завершённых сделок (Deal)."""
    deals = get_user_deals(user_id, session)
    return [
        DealRead(
            id=deal.id,
            swap=map_swap_in_list(deal.swap_request),
            date_time=format_datetime(deal.date_time)
        )
        for deal in deals
    ]
