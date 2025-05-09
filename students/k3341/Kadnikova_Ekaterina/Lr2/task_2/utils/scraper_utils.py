import requests
from fake_useragent import UserAgent
import time
import random
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ScraperUtils:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.update_headers()

    def update_headers(self):
        self.headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive'
        }
        self.session.headers.update(self.headers)

    def get_with_retry(self, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                self.update_headers()
                delay = random.uniform(1, 3)
                time.sleep(delay)

                response = self.session.get(url, timeout=15)

                if response.status_code == 403:
                    logger.warning(f"403 Forbidden for {url}, trying alternative approach...")
                    return self._try_alternative_approach(url)

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

    def _try_alternative_approach(self, url):
        try:
            domain = urlparse(url).netloc
            self.headers.update({
                'Host': domain,
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            })
            return self.session.get(url, timeout=15)
        except Exception as e:
            logger.error(f"Alternative approach failed for {url}: {str(e)}")
            raise


def extract_main_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
        element.decompose()

    main_content = soup.find('main') or soup.find('article') or soup.find('div',
                                                                          class_=lambda x: x and 'content' in x.lower())

    return main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ',
                                                                                               strip=True)