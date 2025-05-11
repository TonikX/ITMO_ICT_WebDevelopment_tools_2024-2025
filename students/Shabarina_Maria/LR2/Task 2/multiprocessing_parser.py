import multiprocessing
import time
from connection import init_db, get_session
from models import News
from base import get_article_text, get_articles, get_topic


def parse_and_save(href, title):
    try:
        full_url = "https://matchtv.ru" + href
        topic_elem = get_topic(full_url)
        topic = topic_elem if topic_elem else "Нет темы"
        result = {
            "url": full_url,
            "title": title,
            "topic": topic,
            "text": get_article_text(full_url)
        }
        with get_session() as session:
            new = News.model_validate(result)
            session.add(new)
            session.commit()
        print(f"[Process] {title} сохранен")
    except Exception as e:
        print(f"[Process Error] № {title}: {e}")


def handle_article_threading(chunk):
    for href, title in chunk:
        parse_and_save(href, title)


def main():
    articles = get_articles()
    num_processes = 4
    step = len(articles) // num_processes
    processes = []

    for i in range(num_processes):
        start = i * step
        if i != num_processes - 1:
            end = (i + 1) * step + 1
        else:
            end = len(articles) + 1
        chunk_data = [(a.get("href"),
                       a.find("div", class_="node-news-list__title").get_text(strip=True) if a.find("div", class_="node-news-list__title") else "Нет заголовка")
                      for a in articles[start:end]]
        process = multiprocessing.Process(target=handle_article_threading, args=(chunk_data,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == "__main__":
    init_db()
    start = time.time()
    main()
    print("Multiprocessing")
    print(f"Время выполнения: {time.time() - start: .2f} сек")
