import requests
import csv
import sys
import time
from bs4 import BeautifulSoup

# Configurações do Proxy Tor
TOR_PROXY = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

# URL do Ahmia na Clearweb (para facilitar o script inicial, mas via Tor)
# Também poderíamos usar o .onion do Ahmia: http://msydqihp2vbt5m36.onion
AHMIA_URL = "https://ahmia.fi/search/"

# Cabeçalhos para evitar bloqueios
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0'
}

def search_ahmia(query):
    print(f"[*] Buscando por: {query}...")
    try:
        params = {'q': query}
        # Usamos SOCKS5H para resolver o DNS via Tor
        response = requests.get(AHMIA_URL, params=params, proxies=TOR_PROXY, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[!] Erro na busca: {e}")
        if "RemoteDisconnected" in str(e) or "Connection aborted" in str(e):
            print("[TIP] O servidor pode ter fechado a conexão. Tente novamente em alguns segundos.")
        return None

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # O Ahmia organiza resultados em <li> dentro da classe 'result'
    for li in soup.find_all('li', class_='result'):
        title_tag = li.find('a')
        snippet_tag = li.find('p')
        
        if title_tag:
            url = title_tag['href'].replace('/search/redirect?search_result=', '').split('&')[0]
            title = title_tag.text.strip()
            snippet = snippet_tag.text.strip() if snippet_tag else "Sem descrição"
            
            # Filtro básico: apenas links .onion
            if ".onion" in url:
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return results

def save_to_csv(results, filename="darkweb_leads.csv"):
    if not results:
        print("[!] Nenhum resultado encontrado para salvar.")
        return

    keys = results[0].keys()
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            # Se o arquivo estiver vazio, escreve o cabeçalho
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(results)
        print(f"[+] {len(results)} resultados salvos em {filename}")
    except Exception as e:
        print(f"[!] Erro ao salvar CSV: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python onion_searcher.py \"termo de busca\"")
        sys.exit(1)
        
    query = " ".join(sys.argv[1:])
    html = search_ahmia(query)
    
    if html:
        results = parse_results(html)
        print(f"[+] Encontrados {len(results)} links .onion.")
        save_to_csv(results)
    else:
        print("[!] Verifique se o serviço do Tor está rodando na porta 9050.")

if __name__ == "__main__":
    main()
