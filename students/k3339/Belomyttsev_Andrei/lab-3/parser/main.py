from fastapi import FastAPI
from pydantic import BaseModel
from database import engine
from parser import parse_and_save
from tasks import parse_and_save_async
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
async def home():
  return {'message': 'Parser works'}

class Url(BaseModel):
  url: str

@app.post('/parse')
async def parse(url: Url):
  parse_and_save(url.url)
  return {'message': 'Parsing completed'}

@app.post('/parse/async')
async def parse_async(url: Url):
  parse_and_save_async.delay(url.url)
  return {'message': 'Parsing started'}