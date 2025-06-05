import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time
from datetime import datetime
from connection import get_async_session
from sqlmodel import select
from models import Task, Priority, Status, Tag, TaskTag, User, pwd_context

REPOSITORIES = [
    "https://github.com/microsoft/vscode",
    "https://github.com/facebook/react",
    "https://github.com/tensorflow/tensorflow",
]


async def ensure_default_user_exists(db_session):
    """Создает пользователя по умолчанию, если он не существует"""
    result = await db_session.execute(select(User).where(User.id == 1))
    user = result.scalar_one_or_none()

    if not user:
        default_user = User(
            id=1,
            username="user1",
            email="user1@example.com",
            hashed_password=pwd_context.hash("password"),
            created_at=datetime.now()
        )
        db_session.add(default_user)
        await db_session.commit()
        print("Created default user with ID 1")
    await db_session.close()

def parse_date(date_str):
    try:
        clean_str = date_str.replace("on ", "").strip()
        return datetime.strptime(clean_str, "%b %d, %Y")
    except ValueError:
        try:
            return datetime.strptime(clean_str, "%B %d, %Y")
        except ValueError:
            return datetime.now()


async def parse_and_save(repo_url: str, session: aiohttp.ClientSession):
    try:
        print(f"Starting parsing {repo_url}")
        issues_url = f"{repo_url}/issues"
        headers = {'User-Agent': 'Mozilla/5.0'}

        async with session.get(issues_url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            db_session = get_async_session()

            await ensure_default_user_exists(db_session)

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
                author_elem = item.select_one('a.issue-item-module__authorCreatedLink--wFZvk')
                author = author_elem.text.strip() if author_elem else "unknown"

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
                    user_id=1
                )
                db_session.add(task)
                await db_session.commit()

                for label in labels:
                    result = await db_session.execute(
                        select(Tag).where(Tag.name == label)
                    )
                    tag = result.scalar_one_or_none()

                    if not tag:
                        tag = Tag(name=label, user_id=1)
                        db_session.add(tag)
                        await db_session.commit()

                    db_session.add(TaskTag(task_id=task.id, tag_id=tag.id))
                await db_session.commit()

            await db_session.close()
        print(f"Successfully processed {repo_url}")
    except Exception as e:
        print(f"Error processing {repo_url}: {str(e)}")


async def main():
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(repo, session) for repo in REPOSITORIES]
        await asyncio.gather(*tasks)

    print(f"Async total time: {time.time() - start_time:.2f} seconds")


if __name__ == '__main__':
    asyncio.run(main())