from celery_worker import celery
import requests

@celery.task(name="tasks.run_parser_task")
def run_parser_task(urls: list[str]):
    try:
        response = requests.post("http://parser:8000/parse", json={"urls": urls})
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}
