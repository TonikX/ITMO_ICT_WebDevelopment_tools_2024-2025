import requests
from bs4 import BeautifulSoup

from parse.db import save_to_db

urls = [
    "https://www.litres.ru/audiobook/aleks-kluchevskoy-leha/13-y-demon-asmodeya-tom-3-71942911/",
    "https://www.litres.ru/book/liya-arden/morana-i-ten-pletuschaya-71735356/",
    "https://www.litres.ru/book/alina-uglickaya-15730401/pervyy-kurs-dlya-popadanki-71594254/",
    "https://www.litres.ru/book/alina-uglickaya-15730401/temnyy-dar-dlya-popadanki-final-71690455/",
    "https://www.litres.ru/book/natalya-kosuhina/pushistoe-schaste-71720077/",
    "https://www.litres.ru/book/dariya-esses/akademiya-505-krah-remali-chast-1-71706193/",
    "https://www.litres.ru/audiobook/nadezhda-mamaeva-5241551/glavnaya-problema-drakona-71963038/",
    "https://www.litres.ru/book/tatyana-serganova/drakona-ne-predlagat-71526211/",
    "https://www.litres.ru/book/anna-sinner/rokovaya-oshibka-diplomata-71400616/",
    "https://www.litres.ru/book/olga-guseynova/lubov-so-smertu-70336537/",
    "https://www.litres.ru/book/olga-guseynova/lubimaya-dlya-monstra-71088157/",
    "https://www.litres.ru/book/matilda-starr/akademiya-mertvyh-dush-nechayannaya-nevesta-65425437/",
    "https://www.litres.ru/book/marina-surzhevskaya-22364624/dikar-63804123/",
    "https://www.litres.ru/book/marina-efiminuk/davay-posporim-71295916/",
    "https://www.litres.ru/book/olga-guseynova/istinnoe-nakazanie-70718458/",
    "https://www.litres.ru/book/natalya-mamleeva/feya-v-akademii-chernogo-drakona-69192982/",
    "https://www.litres.ru/book/denis-makambio/vernut-svoego-byvshego-71629381/",
    "https://www.litres.ru/book/nadezhda-mamaeva-5241551/smotri-ne-pereputay-drakon-71466250/",
    "https://www.litres.ru/book/emili-li/azimar-kuda-privodyat-mechty-68918523/",
    "https://www.litres.ru/book/marina-surzhevskaya-22364624/otrazhenie-ne-menya-iskra-68282110/",
    "https://www.litres.ru/book/natalya-mamleeva/hrustalnaya-tufelka-43-razmera-70573141/",
    "https://www.litres.ru/book/emili-li/azimar-shramy-tvoey-dushi-69242284/",
    "https://www.litres.ru/book/alina-uglickaya-15730401/volki-arbadona-70382353/",
    "https://www.litres.ru/book/emili-li/moya-obitel-69904813/",
    "https://www.litres.ru/book/marina-surzhevskaya-22364624/otrazhenie-ne-menya-serdce-ohharona-68306768/",
    "https://www.litres.ru/book/marina-surzhevskaya-22364624/veyn-55345544/"
]


def chunkify(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")
        full_title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        title, author = parse_title_author(full_title)
        save_to_db(url, title, author)
        print(f"{url} -> title: {title}, author: {author}")
    except Exception as e:
        print(f"Error processing {url}: {e}")


def worker(url_chunk):
    for url in url_chunk:
        parse_and_save(url)


def parse_title_author(full_title: str):
    parts = full_title.split("–")
    main_part = parts[0].strip() if parts else full_title.strip()

    if "," in main_part:
        title_part, author_part = main_part.split(",", 1)
        title = title_part.strip()
        author = author_part.strip()
    else:
        title = main_part
        author = ""

    return title, author
