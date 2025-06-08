from fastapi import APIRouter
from api.v1.users import router as users_router
from api.v1.transactions import router as transactions_router
from api.v1.budgets import router as budgets_router
from api.v1.goals import router as goals_router

# 创建主路由
api_router = APIRouter(prefix="/api/v1")

# 挂载子路由
api_router.include_router(users_router)
api_router.include_router(transactions_router)
api_router.include_router(budgets_router)
api_router.include_router(goals_router)