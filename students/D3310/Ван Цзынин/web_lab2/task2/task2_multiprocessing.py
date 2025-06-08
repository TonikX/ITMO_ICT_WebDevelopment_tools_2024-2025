import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# -------------------------
# 1. 数据库配置（替换为你的真实信息）
# -------------------------
DATABASE_URL = "mysql+mysqlconnector://root:wzn001021@localhost:3306/finance_db"  # lab1 的数据库
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class WebPage(Base):
    __tablename__ = "web_pages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)


# -------------------------
# 2. 核心爬虫逻辑
# -------------------------
def parse_and_save(url):
    """爬取网页标题并保存到数据库"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"

        # 入库操作
        db = SessionLocal()
        page = WebPage(url=url, title=title)
        db.add(page)
        db.commit()
        db.close()

        print(f"Multiprocessing 完成: {url} → {title}")
    except Exception as e:
        print(f"Multiprocessing 失败: {url} → {str(e)}")


# -------------------------
# 3. 多进程调度
# -------------------------
def parallel_crawl_multiprocessing(urls):
    """用 multiprocessing 并行爬取"""
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(parse_and_save, urls)


# -------------------------
# 4. 测速与执行
# -------------------------
if __name__ == "__main__":
    urls = [
        "https://www.example.com",
        "https://www.python.org",
        "https://fastapi.tiangolo.com",
        "https://sqlalchemy.org",
        "https://pydantic.dev"
    ]

    start_time = time.time()
    parallel_crawl_multiprocessing(urls)
    end_time = time.time()

    print(f"\n=== Multiprocessing 结果 ===")
    print(f"总耗时: {end_time - start_time:.2f} 秒")
    print(f"数据库表: web_pages（查看 finance_db 库验证数据）")