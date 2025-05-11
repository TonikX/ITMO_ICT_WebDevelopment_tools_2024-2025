import threading
import time
from connection import init_db, get_session
from models import News
from base import get_article_text, get_articles


def parse_and_save(article):
    try:
        href = article.get("href")
        full_url = "https://matchtv.ru" + href
        title_elem = article.find("div", class_="node-news-list__title")
        title = title_elem.get_text(strip=True) if title_elem else "Нет заголовка"
        topic_elem = article.find_all("li", class_="credits__item")
        topic = topic_elem[1].get_text(strip=True) if topic_elem else "Нет темы"
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
        print(f"[Thread] {title} сохранена")
    except Exception as e:
        print(f"[Thread Error] № {title}: {e}")


def handle_article_threading(chunk):
    for article in chunk:
        parse_and_save(article)


def main():
    articles = get_articles()
    num_threads = 4
    step = len(articles) // num_threads
    threads = []

    for i in range(num_threads):
        start = i * step
        if i != num_threads - 1:
            end = (i + 1) * step + 1
        else:
            end = len(articles) + 1
        t = threading.Thread(target=handle_article_threading, args=(articles[start:end],))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    init_db()
    start = time.time()
    main()
    print("Threading")
    print(f"Время выполнения: {time.time() - start: .2f} сек")
