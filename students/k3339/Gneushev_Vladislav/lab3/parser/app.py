from fastapi import FastAPI, HTTPException
import asyncpg
from parser.db import async_save_bus, ASYNC_DSN
from parser.fetching import async_fetch_html
from parser.parser_utils import parse_car_types_from_html

app = FastAPI(title="Bus Parser API")


@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(ASYNC_DSN)


@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()


@app.post("/parse")
async def parse_url(url: str):
    try:
        html_content = await async_fetch_html(url)
        car_types = parse_car_types_from_html(html_content)
        
        if not car_types:
            raise HTTPException(status_code=404, detail="No bus types found on the page")
            
        await async_save_bus(car_types, app.state.pool)
        
        return {
            "status": "success",
            "message": f"Successfully parsed and saved {len(car_types)} bus types",
            "count": len(car_types)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
