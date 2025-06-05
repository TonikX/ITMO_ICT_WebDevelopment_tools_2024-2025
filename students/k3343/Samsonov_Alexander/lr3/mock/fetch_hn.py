import asyncio
import json

from app.task_manager import hn_client
from app.task_manager.utils import get_http_client

DB_PATH = "db.json"
MAX_POSTS = 100
COMMENT_DEPTH = 3


async def main():
    async with get_http_client() as client:
        new_story_ids = await hn_client.get_top_stories(client)
        if MAX_POSTS:
            new_story_ids = new_story_ids[:MAX_POSTS]

        posts = await hn_client.parse_item_array(new_story_ids, client)

        db = {
            "posts": [],
            "comments": {},
            "posts_new": [],
            "posts_trending": [],
        }

        for post in posts:
            post_id = post["id"]

            db["posts_new"].append(post_id)
            db["posts_trending"].append(post_id)

            db["posts"].append(post)

            comment_tree = await hn_client.traverse_item(post_id, client, depth=COMMENT_DEPTH)
            db["comments"][str(post_id)] = comment_tree.get("kids", [])

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

    print(f"Written to {DB_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
