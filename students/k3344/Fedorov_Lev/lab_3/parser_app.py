from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import subprocess
import asyncio
import os
import sys

app = FastAPI(
    title="Hockey Parser API",
    description="API для парсинга спортивных данных",
    version="1.0.0"
)


class ParseRequest(BaseModel):
    urls: List[HttpUrl]
    parser_type: str = "async"  # async, threading, multiprocessing


class ParseResponse(BaseModel):
    task_id: str
    status: str
    message: str
    teams_parsed: Optional[int] = None
    schools_created: Optional[int] = None
    tournaments_created: Optional[int] = None


task_status = {}


@app.get("/")
async def root():
    return {
        "message": "Hockey Parser API",
        "version": "1.0.0",
        "endpoints": ["/parse", "/status/{task_id}", "/health"]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "parser"}


@app.post("/parse", response_model=ParseResponse)
async def parse_sports_data(
        request: ParseRequest,
        background_tasks: BackgroundTasks
):
    """
    Запускает парсинг спортивных данных
    """
    import uuid
    task_id = str(uuid.uuid4())

    # Определяем какой парсер использовать
    parser_files = {
        "async": "async_parser_sports.py",
        "threading": "threading_parser_sports.py",
        "multiprocessing": "multiprocessing_parser_sports.py"
    }

    parser_file = parser_files.get(request.parser_type, "async_parser_sports.py")
    parser_path = f"/app/parsers/{parser_file}"

    if not os.path.exists(parser_path):
        raise HTTPException(
            status_code=404,
            detail=f"Parser {request.parser_type} not found"
        )

    # Инициализируем статус задачи
    task_status[task_id] = {
        "status": "started",
        "message": f"Parsing started with {request.parser_type} parser",
        "teams_parsed": 0,
        "schools_created": 0,
        "tournaments_created": 0
    }

    # Запускаем парсинг в фоне
    background_tasks.add_task(run_parser_task, task_id, parser_path, request.urls)

    return ParseResponse(
        task_id=task_id,
        status="started",
        message=f"Parsing task started with {request.parser_type} parser"
    )


@app.get("/status/{task_id}", response_model=ParseResponse)
async def get_task_status(task_id: str):
    """
    Получает статус задачи парсинга
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    status = task_status[task_id]
    return ParseResponse(
        task_id=task_id,
        status=status["status"],
        message=status["message"],
        teams_parsed=status.get("teams_parsed"),
        schools_created=status.get("schools_created"),
        tournaments_created=status.get("tournaments_created")
    )


@app.delete("/status/{task_id}")
async def delete_task_status(task_id: str):
    """
    Удаляет статус задачи
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")

    del task_status[task_id]
    return {"message": f"Task {task_id} status deleted"}


async def run_parser_task(task_id: str, parser_path: str, urls: List[HttpUrl]):
    """
    Выполняет парсинг в фоновом режиме
    """
    try:
        # Обновляем статус
        task_status[task_id]["status"] = "running"
        task_status[task_id]["message"] = "Parser is running..."

        env = os.environ.copy()
        env.update({
            "DB_HOST": os.getenv("DB_HOST", "postgres"),
            "DB_NAME": os.getenv("DB_NAME", "hockey_db"),
            "DB_USER": os.getenv("DB_USER", "postgres"),
            "DB_PASSWORD": os.getenv("DB_PASSWORD", "tochange"),
            "PYTHONPATH": "/app"
        })

        process = await asyncio.create_subprocess_exec(
            sys.executable, parser_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd="/app/parsers"
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            # Парсинг успешен
            output = stdout.decode('utf-8')

            # Извлекаем статистику из вывода (простой парсинг)
            teams_parsed = 0
            schools_created = 0
            tournaments_created = 0

            for line in output.split('\n'):
                if 'Total teams parsed:' in line:
                    teams_parsed = int(line.split(':')[1].strip())
                elif 'Total sport schools created:' in line:
                    schools_created = int(line.split(':')[1].strip())
                elif 'Total tournaments created:' in line:
                    tournaments_created = int(line.split(':')[1].strip())

            task_status[task_id].update({
                "status": "completed",
                "message": "Parsing completed successfully",
                "teams_parsed": teams_parsed,
                "schools_created": schools_created,
                "tournaments_created": tournaments_created
            })
        else:
            # Ошибка парсинга
            error_message = stderr.decode('utf-8') if stderr else "Unknown error"
            task_status[task_id].update({
                "status": "failed",
                "message": f"Parsing failed: {error_message[:200]}"
            })

    except Exception as e:
        task_status[task_id].update({
            "status": "failed",
            "message": f"Task execution error: {str(e)}"
        })


@app.get("/tasks")
async def list_tasks():
    """
    Получает список всех задач
    """
    return {"tasks": task_status}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)