from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.models import SwapRequest, Offer, SwapStatus, Ownership, Deal
from app.schemas.swap import SwapCreate, SwapUpdate


def add_swap(user_id: int, swap_create: SwapCreate, session: Session) -> SwapRequest:
    """Создаёт запрос на обмен."""
    get_offer = session.get(Offer, swap_create.get_offer_id)
    if not get_offer:
        raise HTTPException(status_code=404, detail="Requested offer does not exist")
    if not get_offer.is_open:
        raise HTTPException(status_code=400, detail="Requested offer is not available for swap")
    if get_offer.ownership.user_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot request swap for your own offer")

    swap_request = SwapRequest(
        get_offer_id=swap_create.get_offer_id,
        give_offer_id=swap_create.give_offer_id,
        comment=swap_create.comment,
    )
    session.add(swap_request)
    session.commit()
    session.refresh(swap_request)

    return swap_request

def edit_swap(swap: SwapRequest, swap_update: SwapUpdate, session: Session) -> SwapRequest:
    """Обновляет комментарий swap"""
    swap.comment = swap_update.comment
    session.commit()
    session.refresh(swap)
    return swap

def remove_swap(swap: SwapRequest, session: Session):
    """Удаляет swap"""
    session.delete(swap)
    session.commit()

def get_sent_swaps(user_id: int, session: Session, status: SwapStatus | None = None) -> list[SwapRequest]:
    """Возвращает список своп-запросов от пользователя (фильтр по статусу необязателен)."""

    statement = select(SwapRequest).join(Offer, SwapRequest.give_offer_id == Offer.id) \
        .join(Ownership, Offer.ownership_id == Ownership.id) \
        .where(Ownership.user_id == user_id)

    if status:
        statement = statement.where(SwapRequest.status == status)

    return session.exec(statement).all()

def get_received_swaps(user_id: int, session: Session, status: SwapStatus | None = None) -> list[SwapRequest]:
    """Возвращает список своп-запросов к пользователю (фильтр по статусу необязателен)."""

    statement = select(SwapRequest).join(Offer, SwapRequest.get_offer_id == Offer.id) \
        .join(Ownership, Offer.ownership_id == Ownership.id) \
        .where(Ownership.user_id == user_id)

    if status:
        statement = statement.where(SwapRequest.status == status)

    return session.exec(statement).all()

def reject_swap(swap: SwapRequest, session: Session) -> SwapRequest:
    """
    Отклоняет своп-запрос.
    - Проверяет, что своп в статусе PENDING.
    - Устанавливает статус REJECTED.
    """
    swap.status = SwapStatus.REJECTED
    session.commit()
    session.refresh(swap)
    return swap

def accept_swap(swap: SwapRequest, session: Session) -> SwapRequest:
    """
    Принимает своп-запрос:
    1. Меняет статус свопа на COMPLETED.
    2. Закрывает оба оффера.
    3. Оба владения (ownership) делает неактивными (`is_current=False`).
    4. Создаёт новые владения для обмена книгами.
    5. Создаёт запись `Deal`.
    """

    swap.status = SwapStatus.COMPLETED
    session.commit()

    swap.get_offer.is_open = False
    swap.give_offer.is_open = False

    swap.get_offer.ownership.is_current = False
    swap.give_offer.ownership.is_current = False

    new_ownership_1 = Ownership(
        user_id=swap.get_offer.ownership.user_id,
        book_id=swap.give_offer.ownership.book_id,
        is_current=True
    )
    new_ownership_2 = Ownership(
        user_id=swap.give_offer.ownership.user_id,
        book_id=swap.get_offer.ownership.book_id,
        is_current=True
    )

    session.add(new_ownership_1)
    session.add(new_ownership_2)

    deal = Deal(
        swap_id=swap.id,
    )
    session.add(deal)

    session.commit()
    session.refresh(swap)

    return swap
