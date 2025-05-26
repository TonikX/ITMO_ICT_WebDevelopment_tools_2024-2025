import uvicorn
from fastapi import FastAPI

from Lr3.routers import parsers

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, [username]!"


app.include_router(parsers.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)
