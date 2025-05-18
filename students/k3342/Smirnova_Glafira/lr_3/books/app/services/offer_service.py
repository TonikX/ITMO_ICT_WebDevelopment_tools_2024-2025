from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.models import Offer, Ownership, Book, BookGenre, Genre
from app.schemas.offer import OfferUpdate, OfferFilter


def add_offer(ownership_id: int, comment: str, session: Session) -> Offer:
    """Создаёт оффер, если его ещё нет. Если оффер уже существует — ошибка."""
    statement = select(Offer).where(Offer.ownership_id == ownership_id)
    existing_offer = session.exec(statement).first()

    if existing_offer:
        raise HTTPException(status_code=400, detail="Offer already exists for this book")

    offer = Offer(ownership_id=ownership_id, comment=comment)
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer


def edit_offer(offer: Offer, offer_update: OfferUpdate, session: Session) -> Offer:
    """Обновляет комментарий оффера, если он открыт и принадлежит пользователю."""
    offer.comment = offer_update.comment
    session.commit()
    session.refresh(offer)
    return offer


def remove_offer(offer: Offer, session: Session):
    """Удаляет оффер."""
    session.delete(offer)
    session.commit()


def get_offer_by_id(offer_id: int, session: Session) -> Offer:
    """Возвращает оффер по ID."""
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


def get_user_offers(user_id: int, session: Session) -> list[Offer]:
    """Возвращает список всех офферов пользователя."""
    statement = select(Offer).join(Ownership).where((Ownership.user_id == user_id) & Offer.is_open)
    return session.exec(statement).all()


def filter_offers(filter_data: OfferFilter, session: Session):
    """
    Ищет офферы по названию книги, автору, диапазону годов и жанру.
    """
    statement = (
        select(Offer)
        .join(Ownership, Offer.ownership_id == Ownership.id)
        .join(Book, Ownership.book_id == Book.id)
        .where(Offer.is_open)
    )

    if filter_data.name:
        statement = statement.where(Book.name.ilike(f"%{filter_data.name}%"))

    if filter_data.author:
        statement = statement.where(Book.author.ilike(f"%{filter_data.author}%"))

    if filter_data.year_from:
        statement = statement.where(Book.year >= filter_data.year_from)
    if filter_data.year_to:
        statement = statement.where(Book.year <= filter_data.year_to)

    if filter_data.genre:
        statement = (
            statement.join(BookGenre, Book.id == BookGenre.book_id)
            .join(Genre, BookGenre.genre_id == Genre.id)
            .where(Genre.name == filter_data.genre.value)
        )

    if filter_data.user_id:
        statement = statement.where(Ownership.user_id == filter_data.user_id)

    if filter_data.sort_order == "date_asc":
        statement = statement.order_by(Offer.created_at.asc())
    else:
        statement = statement.order_by(Offer.created_at.desc())

    return session.exec(statement).all()