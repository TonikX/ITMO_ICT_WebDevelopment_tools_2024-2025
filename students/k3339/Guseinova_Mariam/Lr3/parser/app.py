from fastapi import FastAPI, HTTPException
import subprocess
import os
import sys
from pydantic import BaseModel, Field, HttpUrl
from typing import List
import asyncio
import json

app = FastAPI()

# Pydantic модель для входящего запроса парсера
class ParserInternalRequest(BaseModel):
    urls: List[HttpUrl] = Field(..., min_length=1) # Ожидаем список HttpUrl
    parser_type: str

def run_blocking_parser(script_path, urls_to_parse):
    # Эта функция будет выполняться в отдельном потоке
    # subprocess.run ждет завершения дочернего процесса
    process = subprocess.run(
        [sys.executable, script_path, *urls_to_parse],
        capture_output=True, # Захватывать stdout и stderr
        text=True,           # Декодировать вывод как текст
        check=False          # Не бросать исключение при ненулевом коде возврата
    )
    parsed_output = {}
    if process.stdout:
        try:
            parsed_output = json.loads(process.stdout)  # Попытка десериализации JSON
        except json.JSONDecodeError:
            # Если stdout не JSON, обрабатываем как обычный текст
            parsed_output = {"raw_output": process.stdout}
    # Возвращаем информацию о завершении
    return {
        "returncode": process.returncode,
        "parsed_data": parsed_output,  # Здесь будут структурированные данные
        "stderr": process.stderr,
        "message": f"Parser {script_path.split('/')[-1]} finished with code {process.returncode}"
    }
@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/parse")
async def run_parser(request: ParserInternalRequest):
    # Преобразуем HttpUrl объекты в строки для subprocess
    urls_to_parse = [str(url) for url in request.urls]
    parser_type = request.parser_type

    valid_parsers = ["async", "threading", "multiprocessing"]
    if parser_type not in valid_parsers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parser type. Choose from {valid_parsers}"
        )

    try:
        script_path = os.path.join(os.path.dirname(__file__), f"{parser_type}_parser.py")

        # Если не дожидаемся завершения процесса, используем subprocess.Popen
        # process = subprocess.Popen(
        #     [sys.executable, script_path, *urls_to_parse],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE
        # )
        # return {"message": f"Parser {parser_type} started successfully for {len(urls_to_parse)} URL(s)."}

        result = await asyncio.to_thread(run_blocking_parser, script_path, urls_to_parse)
        return {"message": "Parser task completed", "details": result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start parser: {str(e)}"
        )