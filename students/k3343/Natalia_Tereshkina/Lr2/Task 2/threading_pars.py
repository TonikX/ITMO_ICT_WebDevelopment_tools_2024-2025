import threading
import time
from connection import init_db, get_session
from models import News
from base import get_articles, parse_article

def parse_and_save(url):
    try:
        article_data = parse_article(url)
        result = {
            "url": article_data["url"],
            "title": article_data["title"],
            "topic": article_data["section"] or "Нет темы",
            "text": article_data["text"]
        }
        with get_session() as session:
            news = News.model_validate(result)
            session.add(news)
            session.commit()
        print(f"[Thread] {article_data['title']} сохранен")
        return True
    except Exception as e:
        print(f"[Thread Error] {url}: {e}")
        return False

def worker(urls):
    for url in urls:
        parse_and_save(url)

def main():
    init_db()
    urls = get_articles(limit=30)
    if not urls:
        print("Нет статей для обработки")
        return

    num_threads = 4
    chunk_size = len(urls) // num_threads
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    threads = []
    for chunk in chunks:
        t = threading.Thread(target=worker, args=(chunk,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Threading время выполнения: {time.time() - start:.2f} сек")