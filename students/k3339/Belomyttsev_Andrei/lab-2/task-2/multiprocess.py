from bs4 import BeautifulSoup
from database import Session
from markdownify import markdownify as md
from models import Post
import random
import time
import requests
from concurrent.futures import ProcessPoolExecutor

def parse_and_save(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  title = soup.title.text
  content = md(soup.article.decode_contents(), heading_style='ATX')
  session = Session()
  session.add(Post(title=title, content=content))
  session.commit()
  print(title)

def main():
  random.seed(161)
  with open('urls.txt') as f:
    urls = [i.strip() for i in f.readlines()]
    random.shuffle(urls)
  
  start_time = time.time()

  with ProcessPoolExecutor() as executor:
    executor.map(parse_and_save, urls)

  end_time = time.time()

  print(f'Time: {end_time - start_time:.2f} seconds')

if __name__ == '__main__':
  main()

# Time: 6.76 seconds