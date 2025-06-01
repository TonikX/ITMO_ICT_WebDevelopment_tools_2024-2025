import multiprocessing
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from connection import engine
from sqlmodel import Session, select
from models import Task, Priority, Status, Tag, TaskTag

REPOSITORIES = [
    "https://github.com/microsoft/vscode",
    "https://github.com/facebook/react",
    "https://github.com/tensorflow/tensorflow",
]


def parse_date(date_str):
    try:
        clean_str = date_str.replace("on ", "").strip()
        return datetime.strptime(clean_str, "%b %d, %Y")
    except ValueError:
        try:
            return datetime.strptime(clean_str, "%B %d, %Y")
        except ValueError:
            return datetime.now()


def parse_and_save(repo_url: str):
    try:
        print(f"Starting parsing {repo_url}")
        issues_url = f"{repo_url}/issues"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(issues_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        session = Session(engine)

        for item in soup.select('.ListItems-module__listItem--Blv7W'):
            title_elem = item.select_one('.IssuePullRequestTitle-module__ListItemTitle_1--_xOfg')
            if not title_elem:
                continue

            title = title_elem.text.strip()
            number_elem = item.select_one('.issue-item-module__defaultNumberDescription--GXzri span')
            issue_number = number_elem.text if number_elem else "unknown"

            labels = [span.get_text(strip=True)
                      for span in
                      item.select('span.Title-module__trailingBadgesContainer--XGsbF span.prc-Text-Text-0ima0')]

            status = "open" if item.select_one('.octicon-issue-opened') else "closed"
            author = item.select_one('a.issue-item-module__authorCreatedLink--wFZvk').text.strip() if item.select_one(
                'a.issue-item-module__authorCreatedLink--wFZvk') else "unknown"

            date_elem = item.select_one('relative-time.sc-aXZVg')
            date_str = date_elem.get_text() if date_elem else datetime.now().strftime("%b %d, %Y")
            date_obj = parse_date(date_str)

            task = Task(
                title=f"{repo_url.split('/')[-1]} #{issue_number}: {title[:100]}",
                description=f"""Issue: {title}
Repository: {repo_url}
Status: {status}
Author: {author}
Created: {date_obj}
Labels: {', '.join(labels)}""",
                priority=Priority.high if 'bug' in labels else Priority.medium,
                status=Status.todo,
                estimated_time_minutes=30,
                user_id=2
            )
            session.add(task)
            session.commit()

            for label in labels:
                tag = session.exec(select(Tag).where(Tag.name == label)).first()
                if not tag:
                    tag = Tag(name=label, user_id=2)
                    session.add(tag)
                    session.commit()
                session.add(TaskTag(task_id=task.id, tag_id=tag.id))
            session.commit()

        print(f"Successfully processed {repo_url}")
    except Exception as e:
        print(f"Error processing {repo_url}: {str(e)}")
    finally:
        session.close()


def main():
    start_time = time.time()

    processes = []
    for repo in REPOSITORIES:
        process = multiprocessing.Process(
            target=parse_and_save,
            args=(repo,)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print(f"Multiprocessing total time: {time.time() - start_time:.2f} seconds")


if __name__ == '__main__':
    main()