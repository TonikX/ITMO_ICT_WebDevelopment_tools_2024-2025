from pydantic import BaseModel
from typing import List, Optional


# 技能模型
class Skill(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""


# 战士模型，包含技能列表
class Warrior(BaseModel):
    id: int
    race: str
    name: str
    level: int
    skills: List[Skill] = []


# 用户模型
class User(BaseModel):
    id: int
    name: str
    email: str
    password: str
    favorite_warriors: List[int] = []  # 存储用户喜欢的战士 ID，实现多对多关系


# 商品模型
class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    price: float
    quantity: int


# 订单条目模型
class OrderItem(BaseModel):
    product_id: int
    quantity: int


# 订单模型
class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]