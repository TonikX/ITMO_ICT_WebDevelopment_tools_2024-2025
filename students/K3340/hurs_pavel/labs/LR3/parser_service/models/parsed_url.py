from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ParsedURL(Base):
    __tablename__ = "parsed_urls"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    title = Column(String, nullable=False)
    parsed_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status = Column(String(50), default="completed")
    task_id = Column(String(255), nullable=True)