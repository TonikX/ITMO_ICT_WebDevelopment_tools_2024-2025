import threading
import requests
from bs4 import BeautifulSoup
import psycopg2
import time


DB_CONFIG = {
    'dbname': 'finance_db',
    'user': 'postgres',
    'password': '123456',
    'host': 'localhost',
    'port': '5434'
}

def insert_user(username, email):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute('INSERT INTO "user" (username, email, hashed_password) VALUES (%s, %s, %s)', (username, email, 'fakepassword'))
        conn.commit()
        cur.close()
        conn.close()
        print(f'User {username} inserted into database')
    except Exception as e:
        print(f'Error inserting user {username}: {e}')

def parse_and_save(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    user_links = soup.find_all('a', class_='tm-user-info__username')

    for user in user_links:
        username = user.text.strip()
        email = f'{username}@habr.fake'
        insert_user(username, email)
        print(f'Parsed user: {username} from {url}')

def parse_with_threading(urls):
    threads = []
    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    urls = [
        'https://habr.com/ru/all/page1/',
        'https://habr.com/ru/all/page2/',
        'https://habr.com/ru/all/page3/',
        'https://habr.com/ru/all/page4/',
        'https://habr.com/ru/all/page5/',
    ]

    start_time = time.time()
    parse_with_threading(urls)
    print(f"Threading time: {time.time() - start_time:.2f} seconds")