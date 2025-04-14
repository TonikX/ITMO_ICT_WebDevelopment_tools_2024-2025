# Таблица для профилей

```python
class Profile:
    id: int = Field(default=None, primary_key=True)
    full_name: str = Field(default="")
    city: str = Field(default="")
    about: str = Field(default="")
    account_id: int = Field(foreign_key="account.id", ondelete="CASCADE")

    account: "Account" = Relationship(
        back_populates="profile",
    )
```