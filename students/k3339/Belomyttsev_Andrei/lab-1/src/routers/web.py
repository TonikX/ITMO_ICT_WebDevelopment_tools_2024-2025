from fastapi import APIRouter, HTTPException
from fastapi import Form, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import db_session
from sqlalchemy.orm.attributes import flag_modified
import markdown
import requests
from routers.auth import user_dependency
from page import page
import models

router = APIRouter(tags=['web'])

templates = Jinja2Templates(directory='templates')

@router.get('/')
async def home(request: Request):
  return templates.TemplateResponse(
    request=request, name='home.html', context={'title': 'band'}
  )

@router.get('/favicon.ico', include_in_schema=False)
async def favicon():
  return FileResponse('resources/favicon.ico')

@router.get('/pages/{page_name}')
async def pages(db: db_session, request: Request, page_name: str):
  try: 
    post = db.query(models.Post).filter(models.Post.slug == page_name.lower()).first()
    return templates.TemplateResponse(
      request=request, name='page.html', context={
        'content': markdown.markdown(post.content, extensions=['markdown.extensions.tables', 'toc']),
        'head': '<style>img{max-height: 500px !important;}</style>',
        'title': post.title
      }
    )
  except Exception as e:
    print(e)
    return page(f'Page not found', 'Page not found')

@router.get('/profile')
async def profile(user: user_dependency, db: db_session):
  if not user:
    raise HTTPException(status_code=401)
  user_db = db.query(models.User).filter(models.User.username == user['username']).first()
  user_db.password = None
  return user_db

@router.get('/privacy')
async def privacy():
  with open('resources/privacy.txt') as f:
    return PlainTextResponse(f.read())