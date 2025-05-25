from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/time_manager_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class URLRequest(BaseModel):
    url: str

class ParseResult(BaseModel):
    url: str
    title: str
    status: str = "completed"

@app.post("/parse", response_model=ParseResult)
async def parse_url(request: URLRequest):
    logger.info(f"Received request to parse URL: {request.url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(request.url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to fetch URL: {response.status}"
                    )
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                title = soup.title.string if soup.title else "No title found"
                title = title.strip()
                
                # Save to database
                db = SessionLocal()
                try:
                    # Using text() for raw SQL with parameters
                    insert_stmt = text("""
                        INSERT INTO parsed_urls (url, title, parsed_at, status)
                        VALUES (:url, :title, :parsed_at, :status)
                    """)
                    
                    db.execute(
                        insert_stmt,
                        {
                            "url": request.url,
                            "title": title,
                            "parsed_at": datetime.utcnow(),
                            "status": "completed"
                        }
                    )
                    db.commit()
                    logger.info(f"Successfully saved parsing result for URL: {request.url}")
                    
                except Exception as db_error:
                    logger.error(f"Database error: {str(db_error)}")
                    db.rollback()
                    raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
                finally:
                    db.close()
                
                return ParseResult(
                    url=request.url,
                    title=title,
                    status="completed"
                )
                
    except aiohttp.ClientError as e:
        logger.error(f"HTTP client error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))