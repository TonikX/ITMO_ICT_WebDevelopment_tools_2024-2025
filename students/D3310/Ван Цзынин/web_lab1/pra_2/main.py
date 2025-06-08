from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .models import Warrior, Skill, User, Product, Order, OrderItem
from typing import List, Optional  # 新增导入 Optional

app = FastAPI(
    title="WebLab2 API",
    description="实践任务：基于 FastAPI 实现相关接口",
    version="1.0.0"
)

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

# 模拟数据库
warriors_db = [
    Warrior(
        id=1,
        race="director",
        name="Мартынов Дмитрий",
        level=12,
        skills=[
            Skill(id=1, name="Купле-продажа компрессоров", description=""),
            Skill(id=2, name="Оценка имущества", description="")
        ]
    ),
    Warrior(
        id=2,
        race="worker",
        name="Андрей Косякин",
        level=12,
        skills=[]
    )
]

users_db = [
    User(id=1, name="John Doe", email="johndoe@example.com", password="password123", favorite_warriors=[1]),
    User(id=2, name="Jane Smith", email="janesmith@example.com", password="secret456", favorite_warriors=[2])
]

products_db = [
    Product(id=1, name="Laptop", description="High-performance laptop", price=999.99, quantity=10),
    Product(id=2, name="Mouse", description="Wireless mouse", price=19.99, quantity=50)
]

orders_db = [
    Order(id=1, user_id=1, items=[OrderItem(product_id=1, quantity=1)]),
    Order(id=2, user_id=2, items=[OrderItem(product_id=2, quantity=2)])
]

# -------------- 战士相关接口 --------------
@app.get("/warriors", response_model=List[Warrior], summary="获取所有战士列表")
async def get_warriors():
    return warriors_db

@app.get("/warrior/{warrior_id}", response_model=Warrior, summary="获取单个战士信息")
async def get_warrior(warrior_id: int):
    for warrior in warriors_db:
        if warrior.id == warrior_id:
            return warrior
    raise HTTPException(status_code=404, detail="Warrior not found")

# -------------- 用户相关接口 --------------
@app.get("/users", response_model=List[User], summary="获取所有用户列表")
async def get_users():
    # 补充用户喜欢的战士详细信息
    for user in users_db:
        favorite_warriors = [w for w in warriors_db if w.id in user.favorite_warriors]
        user.__dict__["favorite_warriors_details"] = favorite_warriors
    return users_db

@app.get("/user/{user_id}", response_model=User, summary="获取单个用户信息")
async def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            favorite_warriors = [w for w in warriors_db if w.id in user.favorite_warriors]
            user.__dict__["favorite_warriors_details"] = favorite_warriors
            return user
    raise HTTPException(status_code=404, detail="User not found")

# -------------- 商品相关接口 --------------
@app.get("/products", response_model=List[Product], summary="获取所有商品列表")
async def get_products():
    return products_db

# -------------- 订单相关接口 --------------
@app.get("/orders", response_model=List[Order], summary="获取所有订单列表")
async def get_orders():
    return orders_db

# -------------- 新增接口示例：根据战士 ID 获取喜欢该战士的用户 --------------
@app.get("/users_by_warrior/{warrior_id}", response_model=List[User], summary="根据战士 ID 获取喜欢该战士的用户")
async def get_users_by_warrior(warrior_id: int):
    result_users = [user for user in users_db if warrior_id in user.favorite_warriors]
    for user in result_users:
        favorite_warriors = [w for w in warriors_db if w.id in user.favorite_warriors]
        user.__dict__["favorite_warriors_details"] = favorite_warriors
    return result_users