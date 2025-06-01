from celery_app import celery_app
from parser import parse_finance_page, save_category
import requests

@celery_app.task(name='parse_task')
def parse_task(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        result = parse_finance_page(url, response.text)
        if result:
            save_category(result)
            return {"status": "success", "data": result}
        return {"status": "error", "message": "Parsing failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}