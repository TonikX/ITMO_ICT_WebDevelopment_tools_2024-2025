import multiprocessing
import time
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from multiprocessing import Queue, Process, Value

from .config import REPOSITORIES, DB_URL, GITHUB_API_URL, GITHUB_TOKEN, MAX_TASKS_PER_REPO
from .db_models import Task, Status, Priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiprocessingParser:
    def __init__(self):
        self.results_queue = Queue()
        self.errors_queue = Queue()
        self.tasks_parsed = Value('i', 0)
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
            
            if MAX_TASKS_PER_REPO is not None:
                issues = issues[:MAX_TASKS_PER_REPO]
            
            for issue in issues:
                title = issue['title']
                description = issue['body']
                status = Status.open if issue['state'] == 'open' else Status.done
                
                task_data = {
                    'summary': title,
                    'description': description,
                    'status': status.value,
                    'priority': Priority.major.value
                }
                
                self.results_queue.put(task_data)
                with self.tasks_parsed.get_lock():
                    self.tasks_parsed.value += 1
                logger.info(f"Parsed task: {title}")
                    
        except Exception as e:
            error_msg = f"Error parsing {repo}: {str(e)}"
            logger.error(error_msg)
            self.errors_queue.put(error_msg)

    def save_to_db(self) -> None:
        engine = create_engine(DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            tasks = []
            while not self.results_queue.empty():
                task_data = self.results_queue.get()
                task = Task(
                    summary=task_data['summary'],
                    description=task_data['description'],
                    status=Status(task_data['status']),
                    priority=Priority(task_data['priority'])
                )
                tasks.append(task)
            
            session.add_all(tasks)
            session.commit()
            logger.info(f"Saved {len(tasks)} tasks to database")
        except Exception as e:
            session.rollback()
            error_msg = f"Error saving to database: {str(e)}"
            logger.error(error_msg)
            self.errors_queue.put(error_msg)
        finally:
            session.close()

    def run(self) -> None:
        start_time = time.time()
        
        processes = []
        for repo in REPOSITORIES:
            process = Process(target=self.parse_repository, args=(repo,))
            processes.append(process)
            process.start()
        
        for process in processes:
            process.join()
        
        self.save_to_db()
        
        self.errors = []
        while not self.errors_queue.empty():
            self.errors.append(self.errors_queue.get())
        
        end_time = time.time()
        logger.info(f"Multiprocessing parser completed in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    parser = MultiprocessingParser()
    parser.run() 