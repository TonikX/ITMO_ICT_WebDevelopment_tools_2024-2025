# Реализованные эндпоинты
1) Book
Создание книги 
http://localhost:8000/book

![html страница](../images/create_book.PNG)
```python
@app.post("/book", response_model=Book)
def create_book(book: BookDefault, session=Depends(get_session)):
    new_book = Book(**book.dict())
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book
```
Получение списка книг
http://localhost:8000/books
![html страница](../images/books.PNG)
```python
@app.get("/books", response_model=List[Book])
def get_books(session=Depends(get_session)):
    books = session.exec(select(Book)).all()
    return books
```

http://localhost:8000/book/{book_id}
![html страница](../images/book_id.PNG)
```python
@app.get("/book/{book_id}", response_model=Book)
def get_book(book_id: int, session=Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
```
2) Остальные модели
Для остальных моделей БД crud запросы реализованы аналогично

![html страница](../images/overview_all.PNG)
```python
@app.get("/offers", response_model=List[Offer])
def get_offers(session=Depends(get_session)):
    offers = session.exec(select(Offer)).all()
    return offers

@app.get("/offer/{offer_id}", response_model=Offer)
def get_offer(offer_id: int, session=Depends(get_session)):
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer

@app.post("/offer", response_model=Offer)
def create_offer(offer: OfferDefault, session=Depends(get_session)):
    new_offer = Offer(**offer.dict(), created_at = datetime.utcnow().isoformat())
    session.add(new_offer)
    session.commit()
    session.refresh(new_offer)
    return new_offer



@app.get("/user_books", response_model=List[UserBook])
def get_user_books(session=Depends(get_session)):
    user_books = session.exec(select(UserBook)).all()
    return user_books

# GET — получение конкретной записи UserBook по id
@app.get("/user_book/{user_book_id}", response_model=UserBook)
def get_user_book(user_book_id: int, session=Depends(get_session)):
    user_book = session.get(UserBook, user_book_id)
    if not user_book:
        raise HTTPException(status_code=404, detail="UserBook not found")
    return user_book

# POST — создание новой связи пользователя с книгой
@app.post("/user_book", response_model=UserBook)
def create_user_book(user_book: UserBookDefault, session=Depends(get_session)):
    new_user_book = UserBook(**user_book.dict())
    session.add(new_user_book)
    session.commit()
    session.refresh(new_user_book)
    return new_user_book


@app.get("/exchanges", response_model=List[Exchange])
def get_exchanges(session=Depends(get_session)):
    exchanges = session.exec(select(Exchange)).all()
    return exchanges

# GET — получение конкретной записи Exchange по id
@app.get("/exchange/{exchange_id}", response_model=Exchange)
def get_exchange(exchange_id: int, session=Depends(get_session)):
    exchange = session.get(Exchange, exchange_id)
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange not found")
    return exchange

# POST — создание новой записи Exchange
@app.post("/exchange", response_model=Exchange)
def create_exchange(exchange: ExchangeDefault, session=Depends(get_session)):
    new_exchange = Exchange(**exchange.dict())
    new_exchange.exchange_date = str(datetime.utcnow())  # Фиксируем дату обмена
    session.add(new_exchange)
    session.commit()
    session.refresh(new_exchange)
    return new_exchange
```
