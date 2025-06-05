from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from parsing_async import parse_and_save

app = FastAPI()

class ParseRequest(BaseModel):
    url: str

@app.post("/parse")
async def parse_url(data: ParseRequest):
    try:
        async with aiohttp.ClientSession() as session:
            await parse_and_save(data.url, session)
        return {"message": f"Successfully parsed and saved data from {data.url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Parser"}

