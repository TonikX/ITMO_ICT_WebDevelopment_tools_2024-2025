from fastapi import FastAPI
from app.routers.tasks import router as tasks_router
from app.models import Lab3Task  # 导入模型
from app.dependencies import engine  # 复用数据库引擎

# 创建 FastAPI 应用
app = FastAPI(
    title="Lab3 FastAPI 实验",
    description="复用 Lab1 数据库，实现任务队列 + 异步处理",
    version="1.0.0"
)

# 注册路由
app.include_router(tasks_router)

# 启动时自动创建表（仅开发环境需要）
from sqlmodel import SQLModel
SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)