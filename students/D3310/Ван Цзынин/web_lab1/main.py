from fastapi import FastAPI
from api.routes import api_router
from sqlmodel import SQLModel
# 直接从 database.py 导入 engine（如果需要）
from dependencies.database import engine

app = FastAPI(
    title="个人财务管理服务",
    description="实现收入/支出记录、预算管理、财务目标追踪",
    version="1.0.0"
)

# 挂载路由
app.include_router(api_router)

# 初始化数据库表（用上面导入的 engine）
SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)