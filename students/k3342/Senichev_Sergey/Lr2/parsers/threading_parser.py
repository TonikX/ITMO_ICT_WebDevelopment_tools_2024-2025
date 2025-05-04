import threading
import time
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from .config import REPOSITORIES, DB_URL, GITHUB_API_URL, GITHUB_TOKEN, MAX_TASKS_PER_REPO
from .db_models import Task, Status, Priority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreadingParser:
    def __init__(self):
        self.engine = create_engine(DB_URL)
        self.Session = sessionmaker(bind=self.engine)
        self.lock = threading.Lock()
        self.results = []
        self.errors = []
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Python-Parser'
        }
        if GITHUB_TOKEN:
            self.headers['Authorization'] = f'token {GITHUB_TOKEN}'

    def parse_repository(self, repo: str) -> None:
        try:
            url = f"{GITHUB_API_URL}/repos/{repo}/issues"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            issues = response.json()
            
            # Apply task limit if specified
            if MAX_TASKS_PER_REPO is not None:
                issues = issues[:MAX_TASKS_PER_REPO]
            
            for issue in issues:
                title = issue['title']
                description = issue['body']
                status = Status.open if issue['state'] == 'open' else Status.done
                
                # Create task object
                task = Task(
                    summary=title,
                    description=description,
                    status=status,
                    priority=Priority.major  # Default priority
                )
                
                with self.lock:
                    self.results.append(task)
                    logger.info(f"Parsed task: {title}")
                    
        except Exception as e:
            error_msg = f"Error parsing {repo}: {str(e)}"
            logger.error(error_msg)
            with self.lock:
                self.errors.append(error_msg)

    def save_to_db(self) -> None:
        session = self.Session()
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

    def run(self) -> None:
        start_time = time.time()
        
        # Create and start threads
        threads = []
        for repo in REPOSITORIES:
            thread = threading.Thread(target=self.parse_repository, args=(repo,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Save results to database
        self.save_to_db()
        
        end_time = time.time()
        logger.info(f"Threading parser completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    parser = ThreadingParser()
    parser.run() 