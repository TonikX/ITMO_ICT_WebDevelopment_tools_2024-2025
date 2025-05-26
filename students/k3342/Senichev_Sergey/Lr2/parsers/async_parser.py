import asyncio
import time
import aiohttp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import ssl
import certifi

from .config import REPOSITORIES, DB_URL, GITHUB_API_URL, GITHUB_TOKEN, MAX_TASKS_PER_REPO
from .db_models import Task, Status, Priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncParser:
    def __init__(self):
        self.results = []
        self.errors = []
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Python-Parser'
        }
        if GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def parse_repository(self, repo: str) -> None:
        try:
            url = f"{GITHUB_API_URL}/repos/{repo}/issues"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, ssl=self.ssl_context) as response:
                    response.raise_for_status()
                    issues = await response.json()
                    
                    if MAX_TASKS_PER_REPO is not None:
                        issues = issues[:MAX_TASKS_PER_REPO]
                    
                    for issue in issues:
                        title = issue['title']
                        description = issue['body']
                        status = Status.open if issue['state'] == 'open' else Status.done
                        
                        task = Task(
                            summary=title,
                            description=description,
                            status=status,
                            priority=Priority.major
                        )
                        
                        self.results.append(task)
                        logger.info(f"Parsed task: {title}")
                    
        except Exception as e:
            error_msg = f"Error parsing {repo}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)

    def save_to_db(self) -> None:
        engine = create_engine(DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            session.add_all(self.results)
            session.commit()
            logger.info(f"Saved {len(self.results)} tasks to database")
        except Exception as e:
            session.rollback()
            error_msg = f"Error saving to database: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
        finally:
            session.close()

    async def run(self) -> None:
        start_time = time.time()
        
        tasks = [self.parse_repository(repo) for repo in REPOSITORIES]
        
        await asyncio.gather(*tasks)
        
        self.save_to_db()
        
        end_time = time.time()
        logger.info(f"Async parser completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    parser = AsyncParser()
    asyncio.run(parser.run()) 