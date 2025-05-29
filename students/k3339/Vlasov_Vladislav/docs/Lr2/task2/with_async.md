Асинхронный подход подразумевает ассинхронное подключение к базам данных и ассинхронные запросы.
В качестве парсера используется BeautifulSoup.

```
async def parse(url: str):
    print(url)
    results = []
    load_dotenv()
    db_url = os.getenv('DB_ADMIN')
    engine = create_async_engine(db_url)
    AsyncSession = async_sessionmaker(bind=engine)

    async with aiohttp.ClientSession() as http_session:
        async with http_session.get(url) as response:
            soup = BeautifulSoup(await response.text(), features="html.parser")

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
                #print("INSERT INTO book (title, author) VALUES (:title, :author)", {"title": title, "author": author}) 

                session = AsyncSession()
                await session.execute(text("INSERT INTO book (title, author) VALUES (:title, :author)"), {"title": title, "author": author})
                await session.commit()
                await session.close()
```

Выбирается 16 страниц с ЛитРес и полученные результаты парсинга записываются в БД