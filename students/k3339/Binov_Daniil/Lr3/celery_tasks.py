from celery_app import app
import requests
from app.crud.tasks import create_task
from app.schemas import TaskCreate
from app.connection import get_session

@app.task
def parse_and_save_task(url: str, user_id: int):
    try:
        parser_url = "http://parser:8001/parse"  
        response = requests.post(parser_url, json=[url])
        response.raise_for_status()
        results = response.json()
        title = results[0]['title'] if results else "No title"

        with get_session() as session:
            task = TaskCreate(title=title, description=url)
            create_task(session, task, user_id)
        return {"status": "success", "url": url, "title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}