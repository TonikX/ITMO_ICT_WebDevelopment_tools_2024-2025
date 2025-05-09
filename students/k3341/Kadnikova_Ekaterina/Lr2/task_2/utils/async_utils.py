import aiohttp
import asyncio
from fake_useragent import UserAgent
import logging
import socket

logger = logging.getLogger(__name__)


class AsyncScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.connector = None

    async def create_session(self):
        try:
            import aiodns
            resolver = aiohttp.AsyncResolver(nameservers=["8.8.8.8", "1.1.1.1"])
            logger.info("Using AsyncResolver with custom DNS servers")
        except ImportError:
            resolver = aiohttp.DefaultResolver()
            logger.warning("aiodns not available, using default system resolver")

        self.connector = aiohttp.TCPConnector(
            resolver=resolver,
            force_close=True,
            enable_cleanup_closed=True,
            ssl=False
        )
        return aiohttp.ClientSession(connector=self.connector)

    async def close(self):
        if self.connector:
            await self.connector.close()

    async def get_with_retry(self, session, url, max_retries=3):
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1'
        }

        for attempt in range(max_retries):
            try:
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 403:
                        logger.warning(f"403 Forbidden for {url}, trying alternative headers...")
                        headers.update({
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Cache-Control': 'no-cache',
                            'Pragma': 'no-cache'
                        })
                        continue

                    response.raise_for_status()
                    return await response.text()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)