from sqlmodel import create_engine
from config.settings import DATABASE_URL

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)