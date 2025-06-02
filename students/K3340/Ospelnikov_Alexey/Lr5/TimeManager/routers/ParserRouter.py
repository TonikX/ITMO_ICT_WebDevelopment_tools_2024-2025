from fastapi import FastAPI, Depends, APIRouter
from models.notification import *
from connection import *
from sqlmodel import Session, select
from typing_extensions import TypedDict
import requests

parserRouter = APIRouter(
    prefix="/parser", tags=['Parser']
)


@parserRouter.get("/parse")
def parse(url: str):
    data = requests.get('http://localhost:9000/parse?url=' + url)
    print(data)
    return data

@parserRouter.get("/parse_async")
async def parse_async(url: str):
    data = await requests.get('http://localhost:9000/parse?url=' + url)
    print(data)
    return data