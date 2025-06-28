from fastapi import FastAPI
from app.api.parser import router as parser_router

app = FastAPI(title="Team Finder API")
app.include_router(parser_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Team Finder API"}