from fastapi import APIRouter, HTTPException
from fastapi import Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import db_session
from sqlalchemy.orm.attributes import flag_modified
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import models
import time
import json
import matplotlib.pyplot as plt
import matplotlib.dates
from utils import genapikey
from routers.auth import user_dependency
from page import page

router = APIRouter(tags=['band'])

templates = Jinja2Templates(directory='templates')

@router.get('/users')
async def get_users(db: db_session):
  users = db.query(models.User).all()
  return [user.username for user in users]

@router.get('/get/{apikey}')
async def get_all(apikey: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  return user.pins

@router.get('/get/{apikey}/{pin}')
async def get_pin(apikey: str, pin: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  return user.pins[pin]

@router.get('/set/{apikey}/{pin}/{val}')
async def set_pin(apikey: str, pin: str, val: int, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  user.pins[pin] = val
  flag_modified(user, 'pins')
  db.commit()
  return {'pin': pin, 'val': val}

@router.get('/plus/{apikey}/{pin}/{val}')
async def plus_pin(apikey: str, pin: str, val: int, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  user.pins[pin] += val
  flag_modified(user, 'pins')
  db.commit()
  return {'pin': pin, 'plus': val}

@router.get('/del/{apikey}/{pin}')
async def del_pin(apikey: str, pin: str, db: db_session):
  user = db.query(models.User).filter(models.User.apikey == apikey).first()
  if not user:
    return PlainTextResponse('Wrong API key')
  del user.pins[pin]
  flag_modified(user, 'pins')
  db.commit()
  return {'deleted': pin}

@router.get('/time')
async def epoch():
  return PlainTextResponse(str(int(time.time())))