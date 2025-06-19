from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter()

class ParseRequest(BaseModel):
    urls: list[str]

@router.post("/start-parse")
def start_parse(request: ParseRequest):
    try:
        response = requests.post("http://parser:8000/parse", json={"urls": request.urls})
        response.raise_for_status()
        return {"message": "Parsing started successfully", "details": response.json()}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))