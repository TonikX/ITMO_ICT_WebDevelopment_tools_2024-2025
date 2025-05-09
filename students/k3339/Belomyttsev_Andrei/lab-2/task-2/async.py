from bs4 import BeautifulSoup
from database import Session
from markdownify import markdownify as md
from models import Post
import random
import time
import asyncio
import aiohttp

async def parse_and_save(url, http_session):
  response = await http_session.get(url)
  soup = BeautifulSoup(await response.text(), 'html.parser')
  title = soup.title.text
  content = md(soup.article.decode_contents(), heading_style='ATX')
  session = Session()
  session.add(Post(title=title, content=content))
  session.commit()
  print(title)

async def gather(urls):
  async with aiohttp.ClientSession() as http_session:
    tasks = []
    for url in urls:
      task = asyncio.create_task(parse_and_save(url, http_session))
      tasks.append(task)
    await asyncio.gather(*tasks)

def main():
  random.seed(161)
  with open('urls.txt') as f:
    urls = [i.strip() for i in f.readlines()]
    random.shuffle(urls)
  
  start_time = time.time()

  asyncio.run(gather(urls))

  end_time = time.time()

  print(f'Time: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
  main()

# Time: 8.30 seconds