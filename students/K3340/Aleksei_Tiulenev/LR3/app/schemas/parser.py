from pydantic import BaseModel
from typing import Optional, Dict, Any

class ParseRequest(BaseModel):
    url: str

class ParseResponse(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    task_id: Optional[str] = None
    message: str
    result: Optional[Dict[str, Any]] = None 