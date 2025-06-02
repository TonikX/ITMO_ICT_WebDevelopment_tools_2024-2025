from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from multiprocessing_parser import run_multiprocessing_parser
from async_parser import run_async_parser
from threading_parser import run_threading_parser
from parser import run_parser

links = [
    'https://www.leadertask.ru/blog/celi-na-etot-god',
    'https://singularity-app.ru/blog/tseli-na-god/?ysclid=maut5kcczr776505947',
    'https://instalook.ru/blog/spisok-celey-na--god?ysclid=mauug5wya098753197',
    'https://www.coaching-online.org/monthly-goals/',
    'https://facedragons.com/personal-development/list-of-goal-ideas/',
    
]

load_dotenv()

sqlalchemy_url = os.environ.get("DATABASE_URL")

def get_sqlalchemy_engine():
    return create_engine(sqlalchemy_url)

def test_connection():
    engine = get_sqlalchemy_engine()
    with engine.connect() as connection:
        print("Подключение к базе данных успешно установлено!")
        
        return True

if __name__ == "__main__":
    test_connection()
    run_parser(sqlalchemy_url, links) 
    run_threading_parser(sqlalchemy_url, links)
    run_multiprocessing_parser(sqlalchemy_url, links)    
    run_async_parser(sqlalchemy_url, links) 
    