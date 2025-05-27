from fastapi import FastAPI, HTTPException, Depends
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.schemas.parser import ParseRequest, ParseResponse
from app.core.database import get_db, init_db
from app.core.cache import get_cache, set_cache
from app.models.parse_result import ParseResult

app = FastAPI(title="Parser Service")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.post("/parse", response_model=ParseResponse)
async def parse_url(request: ParseRequest, db: Session = Depends(get_db)):
    # Check cache first
    cache_key = f"parse_result:{request.url}"
    cached_result = get_cache(cache_key)
    if cached_result:
        return ParseResponse(**cached_result)

    try:
        # Fetch the webpage
        response = requests.get(request.url, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract basic information
        title = soup.title.string if soup.title else None
        
        # Get main content
        main_content = soup.find('main')
        content = main_content.get_text(strip=True) if main_content else None
        
        # Extract metadata
        metadata = {
            'description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None,
            'keywords': soup.find('meta', {'name': 'keywords'})['content'] if soup.find('meta', {'name': 'keywords'}) else None,
            'links': len(soup.find_all('a')),
            'images': len(soup.find_all('img'))
        }
        
        # Create database record
        parse_result = ParseResult(
            url=request.url,
            title=title,
            content=content,
            meta_info=metadata
        )
        db.add(parse_result)
        db.commit()
        db.refresh(parse_result)
        
        # Create response
        response_data = {
            "url": request.url,
            "title": title,
            "content": content,
            "metadata": metadata
        }
        
        # Cache the result
        set_cache(cache_key, response_data)
        
        return ParseResponse(**response_data)
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing content: {str(e)}")

@app.get("/cache/{url:path}")
async def get_cached_result(url: str):
    """Get cached result for URL"""
    cache_key = f"parse_result:{url}"
    result = get_cache(cache_key)
    if result:
        return {"cached": True, "data": result}
    return {"cached": False, "data": None}

@app.get("/history")
async def get_parse_history(db: Session = Depends(get_db)):
    """Get parsing history from database"""
    results = db.query(ParseResult).order_by(ParseResult.created_at.desc()).limit(10).all()
    return [result.to_dict() for result in results] 