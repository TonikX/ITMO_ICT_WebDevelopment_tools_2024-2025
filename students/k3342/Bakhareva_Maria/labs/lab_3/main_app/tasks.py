from celery_main import celery_app
import requests

@celery_app.task(name="tasks.parse_task")
def parse_task():
    parser_url = "http://parser_app:8000/parse"
    try:
        response = requests.post(parser_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
