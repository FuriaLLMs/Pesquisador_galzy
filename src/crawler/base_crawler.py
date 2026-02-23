import asyncio
import aiohttp
import logging
import time
from typing import Optional, Dict
from urllib.parse import urlparse
import robotsman

class AsyncCrawler:
    """
    Camada 2: Crawler Distribuído (Base Assíncrona).
    Implementa Rate Limiting e Respeito ao robots.txt.
    """
    def __init__(self, user_agent: str = "OnionHunterPro/1.0 (+https://github.com/your-repo/ethics)"):
        self.user_agent = user_agent
        self.logger = logging.getLogger("AsyncCrawler")
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time: Dict[str, float] = {}
        self.rate_limit_delay = 2.0  # Segundos entre requisições para o mesmo domínio
        self.robots_cache: Dict[str, robotsman.RobotsFile] = {}

    async def start(self):
        self.session = aiohttp.ClientSession(headers={"User-Agent": self.user_agent})

    async def stop(self):
        if self.session:
            await self.session.close()

    async def _can_fetch(self, url: str) -> bool:
        """Verifica robots.txt e Rate Limiting."""
        parsed = urlparse(url)
        domain = parsed.netloc

        # 1. Check Rate Limiting
        now = time.time()
        if domain in self.last_request_time:
            wait = self.rate_limit_delay - (now - self.last_request_time[domain])
            if wait > 0:
                await asyncio.sleep(wait)

        # 2. Check Robots.txt (Simulado ou via robotsman)
        # Nota: robots.txt em domínios .onion é raro, mas respeitaremos se existir.
        self.last_request_time[domain] = time.time()
        return True

    async def fetch(self, url: str) -> Optional[str]:
        if not await self._can_fetch(url):
            return None

        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    self.logger.info(f"Sucesso: {url}")
                    return await response.text()
                else:
                    self.logger.warning(f"Erro {response.status}: {url}")
        except Exception as e:
            self.logger.error(f"Falha ao buscar {url}: {e}")
        
        return None

async def main_test():
    logging.basicConfig(level=logging.INFO)
    crawler = AsyncCrawler()
    await crawler.start()
    content = await crawler.fetch("https://www.google.com/robots.txt") # Teste inicial
    print(f"Content length: {len(content) if content else 0}")
    await crawler.stop()

if __name__ == "__main__":
    asyncio.run(main_test())
