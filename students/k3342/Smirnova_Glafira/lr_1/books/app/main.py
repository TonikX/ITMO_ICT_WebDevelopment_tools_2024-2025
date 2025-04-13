from fastapi import FastAPI, Request
from app.db.base import init_db
from app.api.routers import router
import logging
from starlette.responses import JSONResponse
app = FastAPI(debug=True)

logging.basicConfig(level=logging.DEBUG)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Ошибка в запросе {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error. See logs for details."}
    )

app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()
