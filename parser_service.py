from fastapi import FastAPI, HTTPException
import asyncio
from lab2.task2.async_parser import process_jobs

app = FastAPI()

@app.post("/parse")
async def parse_jobs(start_id: int = 1, end_id: int = 100):
    try:
        results = await process_jobs(start_id, end_id)
        return {
            "status": "success",
            "message": "Parsing completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)