from fastapi import APIRouter
from database import db_session
from pydantic import BaseModel
import requests
import models

router = APIRouter(tags=['parse'])

class Url(BaseModel):
  url: str

@router.get('/posts')
async def posts(db: db_session):
  return db.query(models.Post).all()

@router.post('/parse')
async def parse(url: Url):
  requests.post('http://parser:8001/parse', json={ 'url': url.url })
  return {'message': 'Parsing completed'}

@router.post('/parse/async')
async def parse_async(url: Url):
  requests.post('http://parser:8001/parse/async', json={ 'url': url.url })
  return {'message': 'Parsing started'}