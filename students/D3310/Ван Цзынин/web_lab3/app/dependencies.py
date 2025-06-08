# 替换原有 redis 导入
import redis  # 直接导入 redis 库
from os import getenv

from sqlalchemy import text
from sqlmodel import create_engine, Session
from celery import Celery  # 若需要在 dependencies 里配置 Celery，可补充

# Redis 相关（修正导入后）
REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL)  # 现在 redis 已定义

# 数据库连接（保持不变）
DATABASE_URL = getenv("DATABASE_URL", "mysql+pymysql://root:wzn001021@localhost/finance_db")
engine = create_engine(DATABASE_URL)

def test_db_connection():
    try:
        with Session(engine) as db:
            result = db.execute(text("SELECT 1"))  # 使用 text 函数声明为文本表达式
            result.fetchone()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

test_db_connection()  # 启动时自动测试
test_db_connection()  # 启动时自动测试
def get_db():
    with Session(engine) as db:
        yield db