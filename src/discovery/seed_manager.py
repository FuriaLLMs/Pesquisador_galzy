import asyncio
import logging
from typing import List, Set

class SeedManager:
    """
    Camada 1: Descoberta de Fontes-Semente.
    Gerencia as URLs iniciais para o crawler.
    """
    def __init__(self):
        self.seeds: Set[str] = set()
        self.logger = logging.getLogger("SeedManager")

    def add_seed(self, url: str):
        if url.startswith(("http://", "https://")):
            self.seeds.add(url)
            self.logger.info(f"Seed adicionada: {url}")

    def load_from_list(self, urls: List[str]):
        for url in urls:
            self.add_seed(url)

    def get_all_seeds(self) -> List[str]:
        return list(self.seeds)

# Exemplo de fontes-semente legítimas (acadêmicas/diretórios públicos)
DEFAULT_SEEDS = [
    "https://v22621.com/onions.txt", # Exemplo de repositório público
    "https://danwin1210.me/onions.php", # Diretório bem conhecido
]
