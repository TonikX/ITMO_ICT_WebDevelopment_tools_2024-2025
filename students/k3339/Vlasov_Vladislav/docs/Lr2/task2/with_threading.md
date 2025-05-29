Многопотчный подход подразумевает синхронное подключение к базам данных и синхронные запросы.
В качестве парсера используется BeautifulSoup.

```
def parse(url: str, results: list):
    print(url)
    load_dotenv()
    db_url = os.getenv('DB_ADMIN').replace('+asyncpg', '')
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")

    books = soup.find_all("div", { "class": "ArtInfo_info__BgoQR"} )

    for book in books:
        try:
            title = book.find("a", { "data-testid": "art__title"}).text
        except:
            title = None
        try:
            author = book.find("a", { "data-testid": "art__authorName"}).text
        except:
            author = None
            
        results.append((title, author))

        session = Session()
        session.execute(text("INSERT INTO book (title, author) VALUES (:title, :author)"), {"title": title, "author": author})
        session.commit()
        session.close()


if __name__ == "__main__":

    start_time = time.perf_counter()
    results = []
    threads: list[threading.Thread] = []

    for url in urls:
        thread = threading.Thread(target=parse, args=(url, results))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
```

Выбирается 16 страниц с ЛитРес и полученные результаты парсинга записываются в БД