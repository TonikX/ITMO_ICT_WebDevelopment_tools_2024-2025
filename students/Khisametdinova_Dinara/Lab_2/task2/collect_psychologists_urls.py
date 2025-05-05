import requests
from bs4 import BeautifulSoup

BASE_URL = "https://en.wikipedia.org"
START_URL = "https://en.wikipedia.org/wiki/List_of_branches_of_psychology"

def collect_urls():
    response = requests.get(START_URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    urls = []

    content = soup.find('div', {'class': 'mw-parser-output'})
    links = content.find_all('a', href=True)

    for link in links:
        href = link['href']
        if href.startswith('/wiki/') and ':' not in href:
            full_url = BASE_URL + href
            urls.append(full_url)

    urls = list(set(urls))  

    with open('specialization_urls.txt', 'w', encoding='utf-8') as f:
        for url in urls:
            f.write(url + '\n')

    print(f"Collected {len(urls)} specialization URLs.")

if __name__ == "__main__":
    collect_urls()
