import logging
from typing import List
import numpy as np
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class EmbeddingGenerator:
    """
    Camada 4: Representação Semântica.
    Transforma texto em vetores numéricos.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.logger = logging.getLogger("EmbeddingGenerator")
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None and SentenceTransformer:
            self.logger.info(f"Carregando modelo: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def generate(self, text: str) -> Optional[np.ndarray]:
        """Gera embedding para um texto."""
        if not self.model or not text:
            self.logger.warning("Modelo não carregado ou texto vazio.")
            return None
        
        try:
            return self.model.encode(text)
        except Exception as e:
            self.logger.error(f"Erro ao gerar embedding: {e}")
            return None

    def generate_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """Gera embeddings para uma lista de textos."""
        if not self.model or not texts:
            return None
        return self.model.encode(texts)

if __name__ == "__main__":
    # Teste (requer sentence-transformers instalado)
    gen = EmbeddingGenerator()
    emb = gen.generate("Exemplo de texto para embedding.")
    if emb is not None:
        print(f"Embedding shape: {emb.shape}")
