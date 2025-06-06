# from enum import Enum
# from typing import Optional, List
# from datetime import datetime, date
# from sqlmodel import SQLModel, Field, Relationship
# from sqlalchemy.dialects.postgresql import ENUM as PGEnum
# from pydantic import BaseModel
# from pydantic import EmailStr

# # ENUM

# class CategoryType(str, Enum):
#     food = "food"
#     transport = "transport"
#     salary = "salary"
#     entertainment = "entertainment"
#     health = "health"
#     other = "other"

# CategoryTypeEnum = PGEnum(CategoryType, name="categorytype", create_type=False)


# # DEFAULT 

# class UserDefault(SQLModel):
#     username: str
#     email: EmailStr = Field(unique=True, index=True)
#     is_active: bool = True
#     hashed_password: str

# class UserCreate(SQLModel):
#     username: str
#     email: EmailStr
#     password: str

# class UserLogin(SQLModel):
#     username: str
#     password: str

# class UserRead(SQLModel):
#     id: int
#     email: EmailStr
#     is_active: bool


# class AccountDefault(SQLModel):
#     user_id: int
#     name: str
#     is_goal: bool = False
#     balance: float 
#     target_amount: Optional[float] = None # цель (только если is_goal=True)



# class TransactionDefault(SQLModel):
#     account_id: int
#     category: CategoryType
#     amount: float
#     description: Optional[str]
#     date: datetime


# class BudgetDefault(SQLModel):
#     user_id: int
#     category: CategoryType
#     month: int
#     year: int
#     limit: float


# class TransferDefault(SQLModel):
#     from_account_id: int
#     to_account_id: int
#     amount: float
#     date: datetime


# # MODELS 

# class User(UserDefault, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)

#     accounts: List["Account"] = Relationship(back_populates="user")
#     budgets: List["Budget"] = Relationship(back_populates="user")


# class Account(AccountDefault, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user.id")

#     user: Optional[User] = Relationship(back_populates="accounts")
#     transactions: List["Transaction"] = Relationship(back_populates="account")

#     transfers_from: List["Transfer"] = Relationship(
#         back_populates="from_account",
#         sa_relationship_kwargs={"foreign_keys": "[Transfer.from_account_id]"}
#     )
#     transfers_to: List["Transfer"] = Relationship(
#         back_populates="to_account",
#         sa_relationship_kwargs={"foreign_keys": "[Transfer.to_account_id]"}
#     )


# class Transaction(TransactionDefault, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     account_id: int = Field(foreign_key="account.id")

#     account: Optional[Account] = Relationship(back_populates="transactions")
#     category: CategoryType


# class Budget(BudgetDefault, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     user_id: int = Field(foreign_key="user.id")

#     user: Optional[User] = Relationship(back_populates="budgets")
#     category: CategoryType


# class Transfer(TransferDefault, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     from_account_id: int = Field(foreign_key="account.id")
#     to_account_id: int = Field(foreign_key="account.id")

#     from_account: Optional[Account] = Relationship(
#         back_populates="transfers_from",
#         sa_relationship_kwargs={"foreign_keys": "[Transfer.from_account_id]"}
#     )
#     to_account: Optional[Account] = Relationship(
#         back_populates="transfers_to",
#         sa_relationship_kwargs={"foreign_keys": "[Transfer.to_account_id]"}
#     )

# class BudgetStats(BaseModel):
#     id: int
#     user_id: int
#     category: CategoryType
#     month: int
#     year: int
#     limit: float
#     spent: float
#     remaining: float