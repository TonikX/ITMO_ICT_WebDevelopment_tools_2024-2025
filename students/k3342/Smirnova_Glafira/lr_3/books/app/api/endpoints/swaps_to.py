from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.swaps import get_current_swap_to_user
from app.api.endpoints.swaps_from import map_swap_full, map_swap_in_list
from app.db.session import get_session
from app.models import SwapRequest
from app.models.models import SwapStatus
from app.schemas.swap import SwapRead, SwapInList, SwapFull
from app.services.swap_service import get_received_swaps, \
    reject_swap, accept_swap

router = APIRouter()

@router.get("/", response_model=list[SwapInList])
def list_received_swaps(user_id: int = Depends(get_current_user), session: Session = Depends(get_session)) -> list[SwapInList]:
    """Возвращает полученные своп-запросы пользователя (любого статуса)."""
    swaps = get_received_swaps(user_id, session)
    return [map_swap_in_list(swap) for swap in swaps]

@router.get("/pending", response_model=list[SwapInList])
def list_received_pending_swaps(user_id: int = Depends(get_current_user), session: Session = Depends(get_session)) -> list[SwapInList]:
    """Возвращает полученные своп-запросы пользователя в статусе PENDING."""
    swaps = get_received_swaps(user_id, session, SwapStatus.PENDING)
    return [map_swap_in_list(swap) for swap in swaps]

@router.patch("/{swap_id}/reject", response_model=SwapRead)
def reject_swap_request(
    swap: SwapRequest = Depends(get_current_swap_to_user),
    session: Session = Depends(get_session)
) -> SwapRequest:
    """Отклоняет своп-запрос (меняет статус на REJECTED)."""
    if swap.status != SwapStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending swaps can be rejected")
    return reject_swap(swap, session)

@router.patch("/{swap_id}/accept", response_model=SwapRead)
def accept_swap_request(
    swap: SwapRequest = Depends(get_current_swap_to_user),
    session: Session = Depends(get_session)
) -> SwapRequest:
    """Принимает своп-запрос (меняет статус на COMPLETED и выполняет обмен книг)."""
    if swap.status != SwapStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending swaps can be accepted")
    return accept_swap(swap, session)

@router.get("/{swap_id}", response_model=SwapFull)
def retrieve_received_swap(
    swap: SwapRequest = Depends(get_current_swap_to_user),
) -> SwapFull:
    """Возвращает один полученный своп-запрос с полной информацией."""
    return map_swap_full(swap)

