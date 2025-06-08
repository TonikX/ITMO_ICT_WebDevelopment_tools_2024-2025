from sqlmodel import Session, create_engine
from fastapi import Depends

# 硬编码数据库连接字符串（直接写死，不用.env）
DATABASE_URL = "mysql+mysqlconnector://root:wzn001021@localhost:3306/finance_db"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """获取数据库会话的依赖函数"""
    with Session(engine) as session:
        yield session