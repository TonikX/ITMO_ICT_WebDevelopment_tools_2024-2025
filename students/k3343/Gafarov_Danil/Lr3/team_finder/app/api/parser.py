from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter()

class ParseRequest(BaseModel):
    url: str

@router.post("/parse")
def run_parser(req: ParseRequest):
    try:
        parser_url = "http://parser:8000/parse"
        response = requests.post(parser_url, json={"url": req.url})

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка при вызове парсера")

        return {"parser_response": response.json()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Не удалось связаться с парсером: {str(e)}")