import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine

from config import settings
from db.models import Base
from db.database import engine
from rest.task.router import router as task_router
from rest.sprint.router import router as sprint_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Management API",
    description="API для управления задачами и спринтами с интеграцией парсера",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)
app.include_router(sprint_router)


class ParseRequest(BaseModel):
    repositories: List[str]


class ParseResponse(BaseModel):
    message: str
    task_id: str = None
    repositories: List[str]


@app.get("/")
def read_root():
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "endpoints": {
            "tasks": "/tasks/",
            "sprints": "/sprints/",
            "parse": "/parse",
            "parse_async": "/parse/async"
        }
    }


@app.post("/parse", response_model=ParseResponse)
def parse_repositories(request: ParseRequest):
    try:
        parser_url = "http://parser:8001/parse"
        response = requests.post(
            parser_url,
            json={"repositories": request.repositories},
            timeout=300
        )
        response.raise_for_status()
        
        result = response.json()
        return ParseResponse(
            message="Parsing completed successfully",
            repositories=request.repositories
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Parser service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/parse/async", response_model=ParseResponse)
def parse_repositories_async(request: ParseRequest):
    try:
        parser_url = "http://parser:8001/parse/async"
        response = requests.post(
            parser_url,
            json={"repositories": request.repositories},
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        return ParseResponse(
            message="Parsing task queued successfully",
            task_id=result.get("task_id"),
            repositories=request.repositories
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Parser service error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "task-management-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 