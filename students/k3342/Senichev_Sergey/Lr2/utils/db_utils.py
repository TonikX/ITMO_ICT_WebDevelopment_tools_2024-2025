from sqlalchemy import create_engine, Column, Integer, String, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class WebPage(Base):
    __tablename__ = 'web_pages'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    title = Column(String(500))
    content = Column(Text)
    parsing_method = Column(String(50))  # Метод парсинга (threading/multiprocessing/async)
    parsing_time = Column(Float)  # Время парсинга в секундах

def init_db():
    """Инициализирует базу данных и создает таблицы."""
    # Создаем папку db, если она не существует
    os.makedirs('db', exist_ok=True)
    engine = create_engine('sqlite:///db/web_pages.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def save_page(session, url: str, title: str, content: str = None, parsing_method: str = None, parsing_time: float = None):
    """Сохраняет веб-страницу в базу данных."""
    page = WebPage(
        url=url, 
        title=title, 
        content=content,
        parsing_method=parsing_method,
        parsing_time=parsing_time
    )
    session.add(page)
    session.commit()
    return page 