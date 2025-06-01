from fastapi import FastAPI

from parser.parse import ParseRequest
from parser.parser import run_parser

app = FastAPI()


@app.post("/parse")
async def parse_url(parse_request: ParseRequest):
    print(parse_request.urls)
    print(f"Parsing URLS: {parse_request.urls}")
    await run_parser(parse_request.urls)
    return {"message": "Parsing completed"}
