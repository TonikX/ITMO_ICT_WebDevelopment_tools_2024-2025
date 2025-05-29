from fastapi import FastAPI, HTTPException
from parser import parse_and_save_page
import requests
from models import ParseRequest
from celery_config import celery_app, parse_from_url


app = FastAPI()

@app.post("/parse")
def parse_url(data: ParseRequest):
    try:
        response = requests.get(url)
        response.raise_for_status()
        hackathon = parse_and_save_page(response.text)
        return {"hackathon": hackathon}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-trigger")
async def trigger_parse(data: ParseRequest):
    task = parse_from_url.delay(data.url)
    return {"message": "Parse task started", "task_id": task.id}


# urls = [
#     'https://www.хакатоны.рус/tpost/0kblp5ouv1-vnedreid',
#     'https://www.хакатоны.рус/tpost/o5y3kpvtj1-architech',
#     'https://www.хакатоны.рус/tpost/80uis0egp1-go-ctf-2025',
#     'https://www.хакатоны.рус/tpost/yd4yk40ta1-forum',
#     'https://www.хакатоны.рус/tpost/eculsok1x1-unithack-2025',
#     'https://www.хакатоны.рус/tpost/dp1t70lav1-tech-squad-missiya-ii',
#     'https://www.хакатоны.рус/tpost/3i2n66z1y1-kiberhak',
#     'https://www.хакатоны.рус/tpost/imklbzv241-belie-hakeri',
#     'https://www.хакатоны.рус/tpost/1fhvmnaa81-gorod-geroev'
# ]