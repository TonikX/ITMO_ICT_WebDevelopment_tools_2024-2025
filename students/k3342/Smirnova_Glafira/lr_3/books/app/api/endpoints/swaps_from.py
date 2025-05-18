from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.offers import get_current_offer
from app.api.dependencies.swaps import get_current_swap_from_user
from app.db.session import get_session
from app.models import SwapRequest
from app.models.models import SwapStatus
from app.schemas.info import MessageResponse
from app.schemas.swap import SwapCreate, SwapRead, SwapUpdate, SwapInList, SwapFull
from app.services.swap_service import add_swap, edit_swap, remove_swap, get_sent_swaps
from app.utils.mapper import map_swap_in_list, map_swap_full

router = APIRouter()

@router.post("/", response_model=SwapRead, status_code=201)
def create_swap(
        swap_create: SwapCreate,
        user_id: int = Depends(get_current_user),
        session: Session = Depends(get_session)
) -> SwapRequest:
    """Создаёт своп-запрос."""
    get_current_offer(swap_create.give_offer_id, user_id, session)
    return add_swap(user_id, swap_create, session)

@router.patch("/{swap_id}", response_model=SwapRead)
def update_swap(
    swap_update: SwapUpdate,
    swap=Depends(get_current_swap_from_user),
    session: Session = Depends(get_session)
)-> SwapRequest:
    """Обновляет комментарий своп-запроса."""
    if swap.status != SwapStatus.PENDING:
        raise HTTPException(status_code=400, detail="Swap request is not pending")
    return edit_swap(swap, swap_update, session)

@router.delete("/{swap_id}", response_model=MessageResponse)
def delete_swap(
    swap = Depends(get_current_swap_from_user),
    session: Session = Depends(get_session)
) -> MessageResponse:
    """Удаляет своп-запрос."""
    if (swap.status == SwapStatus.ACCEPTED) | (swap.status == SwapStatus.COMPLETED):
        raise HTTPException(status_code=400, detail="Swap request was already accepted")
    remove_swap(swap, session)
    return MessageResponse(message="Swap request deleted successfully")

@router.get("/", response_model=list[SwapInList])
def list_sent_swaps(user_id: int = Depends(get_current_user), session: Session = Depends(get_session)) -> list[SwapInList]:
    """Возвращает отправленные своп-запросы пользователя (любого статуса)."""
    swaps = get_sent_swaps(user_id, session)
    return [map_swap_in_list(swap) for swap in swaps]

@router.get("/pending", response_model=list[SwapInList])
def list_sent_pending_swaps(user_id: int = Depends(get_current_user), session: Session = Depends(get_session)) -> list[SwapInList]:
    """Возвращает отправленные своп-запросы пользователя в статусе PENDING."""
    swaps = get_sent_swaps(user_id, session, SwapStatus.PENDING)
    return [map_swap_in_list(swap) for swap in swaps]

@router.get("/{swap_id}", response_model=SwapFull)
def retrieve_sent_swap(
    swap: SwapRequest = Depends(get_current_swap_from_user),
) -> SwapFull:
    """Возвращает один отправленный своп-запрос с полной информацией."""
    return map_swap_full(swap)
