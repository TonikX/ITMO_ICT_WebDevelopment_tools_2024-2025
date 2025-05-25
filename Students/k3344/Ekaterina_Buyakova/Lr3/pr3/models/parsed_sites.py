from sqlalchemy import Column, Integer, String
from models.base import Base


class ParsedSites(Base):
    __tablename__ = "parsed_sites"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String)
