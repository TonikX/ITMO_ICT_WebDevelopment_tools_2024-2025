import requests
from bs4 import BeautifulSoup
import csv

# URL to scrape
url = "https://habr.com/ru/flows/admin/articles/top/yearly/"

# Define headers to make the request appear like it came from a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()  # Will raise an exception if there's an error in the request

# Parse the page with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")
# print(soup.prettify())

a_s = soup.find_all("a", class_="tm-title__link")
print (len(a_s))
for i in range (len(a_s)-2):
    print("https://habr.com"+a_s[i]['href'])
    print ("\n") if (i%6)==0 and i!=0 else ()



