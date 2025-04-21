from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class WebPage(Base):
    __tablename__ = 'web_pages'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    title = Column(String(500))
    content = Column(Text)

def init_db():
    """Инициализирует базу данных и создает таблицы."""
    engine = create_engine('sqlite:///web_pages.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def save_page(session, url: str, title: str, content: str = None):
    """Сохраняет веб-страницу в базу данных."""
    page = WebPage(url=url, title=title, content=content)
    session.add(page)
    session.commit()
    return page 