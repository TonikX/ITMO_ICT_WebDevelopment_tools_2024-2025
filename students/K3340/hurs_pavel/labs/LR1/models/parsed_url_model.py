from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ParsedURL(SQLModel, table=True):
    __tablename__ = "parsed_urls"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="completed")
    task_id: Optional[str] = Field(default=None)  # For async tasks