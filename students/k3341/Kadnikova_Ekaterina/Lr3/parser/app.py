from fastapi import APIRouter, HTTPException
import requests
from connection import get_session
from models.category import Category
import logging

from parser import save_category, parse_finance_page

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/parse")
async def parse_url(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        result = parse_finance_page(url, response.text)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to parse page content")

        save_category(result)

        return {
            "status": "success",
            "data": result,
            "source": url
        }

    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")