import logging
from typing import Optional
from langdetect import detect, DetectorFactory

# Garantir resultados determinísticos na detecção de idioma
DetectorFactory.seed = 0

class LanguageDetector:
    """
    Camada 3: Detecção de Idioma.
    """
    def __init__(self):
        self.logger = logging.getLogger("LanguageDetector")

    def detect_language(self, text: str) -> str:
        """Retorna o código do idioma (ex: 'pt', 'en')."""
        if not text or len(text) < 20:
            return "unknown"
        
        try:
            return detect(text)
        except Exception as e:
            self.logger.warning(f"Falha ao detectar idioma: {e}")
            return "unknown"

if __name__ == "__main__":
    detector = LanguageDetector()
    print(f"Idioma: {detector.detect_language('Isso é um teste em português.')}")
    print(f"Idioma: {detector.detect_language('This is an English test.')}")
