import multiprocessing
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
        print(f"[Process] {article_data['title']} сохранен")
        return True
    except Exception as e:
        print(f"[Process Error] {url}: {e}")
        return False

def worker(urls):
    init_db()
    for url in urls:
        parse_and_save(url)

def main():
    urls = get_articles(limit=30)
    if not urls:
        print("Нет статей для обработки")
        return

    num_processes = 4
    chunk_size = len(urls) // num_processes
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=worker, args=(chunk,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Multiprocessing время выполнения: {time.time() - start:.2f} сек")