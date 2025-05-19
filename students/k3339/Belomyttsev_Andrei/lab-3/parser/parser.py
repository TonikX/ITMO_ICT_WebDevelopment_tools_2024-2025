from bs4 import BeautifulSoup
from database import Session
from markdownify import markdownify as md
from models import Post
import requests

def parse_and_save(url):
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  title = soup.title.text
  content = md(soup.article.decode_contents(), heading_style='ATX')
  session = Session()
  session.add(Post(title=title, content=content))
  session.commit()
  return title