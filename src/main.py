import logging
from typing import Dict, Any, Optional
from src.discovery.seed_manager import SeedManager
from src.crawler.base_crawler import AsyncCrawler
from src.normalization.parser import ContentParser
from src.normalization.language_det import LanguageDetector
from src.semantics.embeddings import EmbeddingGenerator

class OnionHunterCoordinator:
    """
    Coordenador Principal do Sistema (Orquestrador).
    Conecta todas as camadas profissionais.
    """
    def __init__(self):
        self.logger = logging.getLogger("OnionHunterPro")
        self.crawler = AsyncCrawler()
        self.parser = ContentParser()
        self.lang_det = LanguageDetector()
        self.emb_gen = EmbeddingGenerator()
        self.results = []

    async def process_url(self, url: str) -> Optional[Dict[str, Any]]:
        self.logger.info(f"Processando: {url}")
        
        # L2: Fetch
        html = await self.crawler.fetch(url)
        if not html:
            return None

        # L3: Normalize
        clean_text = self.parser.clean_html(html)
        metadata = self.parser.extract_metadata(html)
        lang = self.lang_det.detect_language(clean_text)

        # L4: Semantic representation
        embedding = self.emb_gen.generate(clean_text)

        result = {
            "url": url,
            "metadata": metadata,
            "language": lang,
            "text_preview": clean_text[:200],
            "embedding": embedding.tolist() if embedding is not None else None
        }
        
        return result

    async def run_discovery(self, seeds: list):
        await self.crawler.start()
        for seed in seeds:
            res = await self.process_url(seed)
            if res:
                self.results.append(res)
        await self.crawler.stop()
        self.logger.info(f"Coleta finalizada. {len(self.results)} sucessos.")

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    
    seeds = ["https://v22621.com/onions.txt"] # Exemplo
    coordinator = OnionHunterCoordinator()
    asyncio.run(coordinator.run_discovery(seeds))
