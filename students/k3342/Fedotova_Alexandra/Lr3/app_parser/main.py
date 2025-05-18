from fastapi import FastAPI
from pydantic import BaseModel
from .parser_logic import run_parser

app = FastAPI()

class ParserRequest(BaseModel):
    urls: list[str]

@app.post("/parse")
def parse(request: ParserRequest):
    return run_parser(request.urls)
