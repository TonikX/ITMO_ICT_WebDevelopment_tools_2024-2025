from fastapi import APIRouter, HTTPException, Query
import requests

router = APIRouter()

@router.post("/trigger-parse")
def trigger_parse():
    parser_url = "http://parser_app:8000/parse"

    try:
        response = requests.post(parser_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при вызове парсера: {e}")
