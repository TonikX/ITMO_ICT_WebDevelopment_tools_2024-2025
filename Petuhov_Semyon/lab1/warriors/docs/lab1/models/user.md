# User 
Класс для создания модели 
```python
class UserDefault(SQLModel):
    username: str
    email: str
    about_me: Optional[str] = None
```
Сама модель
```python
class User(UserDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: Optional[str] = None
    books: List["UserBook"] = Relationship(back_populates="user")
    sent_offers: List["Offer"] = Relationship(back_populates="sender", sa_relationship_kwargs={"foreign_keys": "Offer.sender_id"})
    received_offers: List["Offer"] = Relationship(back_populates="receiver", sa_relationship_kwargs={"foreign_keys": "Offer.receiver_id"})

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
```
Модель UserDefault нужна для более удобной реализации POST запроса. Сама модель содержит списки книг для этого пользователя и функции
для аутентификации
