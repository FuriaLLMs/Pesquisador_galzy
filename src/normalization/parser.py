from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging
import re

class ContentParser:
    """
    Camada 3: Normalização de Dados.
    Extração de texto, limpeza de HTML e extração de metadados.
    """
    def __init__(self):
        self.logger = logging.getLogger("ContentParser")

    def clean_html(self, html_content: str) -> str:
        """Remove scripts, estilos e extrai texto limpo."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remover elementos indesejados
        for element in soup(["script", "style", "header", "footer", "nav"]):
            element.decompose()

        # Extrair texto
        text = soup.get_text(separator=' ')
        
        # Limpar espaços em branco excessivos
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def extract_metadata(self, html_content: str) -> Dict[str, str]:
        """Extrai título e meta tags."""
        soup = BeautifulSoup(html_content, 'html.parser')
        metadata = {
            "title": soup.title.string if soup.title else "No Title",
            "description": "",
            "keywords": ""
        }

        # Meta tags
        description = soup.find("meta", attrs={"name": "description"})
        if description:
            metadata["description"] = description.get("content", "")

        keywords = soup.find("meta", attrs={"name": "keywords"})
        if keywords:
            metadata["keywords"] = keywords.get("content", "")

        return metadata

# Teste simples
if __name__ == "__main__":
    test_html = "<html><head><title>Test Page</title></head><body><script>alert(1)</script><h1>Hello World</h1><p>This is a test.</p></body></html>"
    parser = ContentParser()
    print(f"Clean text: {parser.clean_html(test_html)}")
    print(f"Metadata: {parser.extract_metadata(test_html)}")
