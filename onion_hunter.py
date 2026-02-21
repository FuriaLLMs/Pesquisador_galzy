import requests
import csv
import sys
import time
import argparse
import json
import os
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

# --- Configurações de Banco de Dados e Persistência ---
DB_FILE = "onion_knowledge_base.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_to_db(new_results):
    db = load_db()
    added = 0
    for r in new_results:
        url = r['url']
        if url not in db:
            db[url] = {
                'title': r['title'],
                'category': r['category'],
                'first_seen': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source': r['source']
            }
            added += 1
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    return added

def fts_search(query):
    """Realiza uma busca full-text local na Base de Conhecimento"""
    db = load_db()
    results = []
    q = query.lower()
    for url, data in db.items():
        if q in url.lower() or q in data['title'].lower() or q in data['category'].lower():
            results.append({'url': url, **data})
    
    if results:
        print(f"\n[FTS] Encontrados {len(results)} resultados locais para '{query}':")
        for r in results:
            print(f"- [{r['category']}] {r['title']} | {r['url']}")
    else:
        print(f"\n[FTS] Nenhum resultado local para '{query}'.")
TOR_PROXIES = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

import random
from stem import Signal
from stem.control import Controller

# --- Configurações de Anonimato e Ofuscação (v6.0) ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0'
]

def rotate_tor_circuit():
    """Tenta renovar o circuito (IP) do Tor via sinal NEWNYM"""
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()  # Requer ControlPort configurado no Tor
            controller.signal(Signal.NEWNYM)
            print("[PHANTOM] Circuito Tor renovado com sucesso.")
    except Exception as e:
        pass # Falha silenciosa se o ControlPort não estiver ativo

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }

def jitter():
    """Atraso aleatório para simular comportamento humano"""
    time.sleep(random.uniform(0.5, 2.5))

# --- Configurações de Busca e Categorização (Modo Babel v5.1) ---
SYNONYMS = {
    'armas': [
        'weapons', 'firearms', 'guns', 'pistol', 'rifle', 'munition', 'armament', # EN
        'оружие', 'пистолет', 'винтовка', 'боеприпасы', # RU
        '武器', '枪', '步枪', '弹药', # ZH
        'أسلحة', 'مسدس', 'بندقية', 'ذخيرة', # AR
        'armas de fuego', 'pistola', 'fusil', 'munición', # ES
        'armes', 'pistolet', 'fusil', 'munitions' # FR
    ],
    'weapons': [
        'armas', 'firearms', 'guns', 'pistol', 'rifle', 'munition', 'armament',
        'оружие', 'пистолет', 'винтовка', 'боеприпасы',
        '武器', '枪', '步枪', '弹药'
    ],
    'drugs': ['drogas', 'narcotics', 'cannabis', 'cocaine', 'heroin', 'pills', 'наркотики', '毒品'],
    'police': ['policia', 'law enforcement', 'cop', 'intel', 'intelligence', 'полиция', '警方']
}

CATEGORIES = {
    'Armamento': ['arma', 'gun', 'weapon', 'firearm', 'ammo', 'explosive', 'balístico', 'оружие', '武器', 'أسلحة'],
    'Financeiro': ['carding', 'cc', 'bitcoin', 'wallet', 'money', 'paypal', 'dump', 'banco', 'transferência', 'money laundering'],
    'Narcóticos': ['drugs', 'cannabis', 'cocaine', 'lsd', 'mdma', 'heroin', 'opioid', 'drogas', 'farma', 'наркотики', '毒品'],
    'Serviços OSINT': ['wiki', 'directory', 'search', 'index', 'links', 'links list', 'agregador'],
    'Fóruns/Social': ['forum', 'chat', 'board', 'community', 'mail', 'messaging', 'social'],
    'Segurança/Intel': ['security', 'privacy', 'intel', 'intelligence', 'police', 'hack', 'leaked', 'exploit', 'полиция']
}

def get_category(text, url=""):
    text = (text + " " + url).lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            return cat
    return "Outros / Geral"

# --- Motores de Busca e Endereços (V3 atualizados 2025/2026) ---
ENGINES = {
    'ahmia_onion': 'http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/',
    'ahmia_clear': 'https://ahmia.fi/search/',
    'duckduckgo': 'https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfima3ogsn36cyq6wiid.onion/html/',
    'hidden_wiki_mirrors': [
        'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otj3cy6ih7eypbad.onion/wiki/Main_Page',
        'http://onionlinksy7q6ieitv52v3on73g37x7q6ieitv52v3on73g37x7q6ie.onion/',
        'http://torlinksge6enmcyy.onion/',
        'http://dirnxxdraygbifgc.onion/'
    ],
    'torch': 'http://torchde36iab4v3y.onion/',
    'haystak': 'http://haystak5njsmn2hkad5id6ba2y7vbtmk36h6pkgpboxixp4dpciy2id.onion/'
}

# --- Fontes de Sementes (Seeds) e Feeds Massivos ---
FEEDS_URLS = [
    'https://raw.githubusercontent.com/nemo-nesciam/2024.onion.links/main/Hidden-Wiki.txt',
    'https://raw.githubusercontent.com/MTXPr0ject/Dark-Web-Links/refs/heads/main/README.md',
    'https://gist.githubusercontent.com/mvelazc0/23249033f99e691238d2/raw/hidden_services_urls.txt',
    'https://raw.githubusercontent.com/pali-justin/Dark-Web-Links/master/Dark-Web-Links.md',
    'https://raw.githubusercontent.com/fastfire/deep-dark-quotes/master/README.md',
    'https://raw.githubusercontent.com/billytheking/Onion-Links/master/links.txt',
    'https://raw.githubusercontent.com/v2ray/domain-list-community/master/data/onion',
    'https://raw.githubusercontent.com/not-not-evil/onion-links/main/links.txt',
    'https://raw.githubusercontent.com/alecmuffett/real-world-onion-sites/master/README.md',
    'https://raw.githubusercontent.com/S-9/Secret_Deep_Web_Links/master/Secret_Deep_Web_Links.md'
]

class BaseEngine:
    def __init__(self, name, url, fetch_all=False):
        self.name = name
        self.url = url
        self.fetch_all = fetch_all
        self.results = []

    def search(self, query):
        raise NotImplementedError

class DeepCrawler(BaseEngine):
    """Navega nos links encontrados para descobrir novos links dentro deles"""
    def __init__(self, name, url, fetch_all=False, depth=1):
        super().__init__(name, url, fetch_all)
        self.depth = depth
        self.visited = set()

    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        try:
            jitter()
            r = requests.get(self.url, proxies=TOR_PROXIES, headers=get_random_headers(), timeout=30)
            if r.status_code == 200:
                import re
                content = r.text.lower()
                onions = list(set(re.findall(r'[a-z2-7]{56}\.onion|[a-z2-7]{16}\.onion', content)))
                for onion in onions:
                    url = f"http://{onion}/"
                    category = get_category(content, url)
                    if self.fetch_all:
                        self.results.append({'title': 'Deep Discovery', 'url': url, 'source': 'Crawler', 'category': category})
                    else:
                        for kw in keywords:
                            if kw.lower() in content or kw.lower() in onion:
                                self.results.append({'title': f'Deep Match: {kw}', 'url': url, 'source': 'Crawler', 'category': category})
                                break
                if self.results:
                    print(f"[CRAWL] {self.name} encontrou {len(self.results)} links em {self.url[:30]}...")
        except:
            pass

class AhmiaEngine(BaseEngine):
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        for kw in keywords:
            try:
                jitter()
                params = {'q': kw}
                r = requests.get(self.url, params=params, proxies=TOR_PROXIES, headers=get_random_headers(), timeout=45)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    count = 0
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if '.onion' in href and 'ahmia.fi' not in href:
                            url = href.split('search_result=')[-1].split('&')[0] if 'redirect' in href else href
                            url = url.replace('%3A', ':').replace('%2F', '/')
                            if '.onion' in url and 'juhanurmi' not in url:
                                title = a.text.strip() or f"Match: {kw}"
                                category = get_category(title, url)
                                self.results.append({
                                    'title': title[:100], 
                                    'url': url, 
                                    'source': self.name,
                                    'category': category
                                })
                                count += 1
                    if count: print(f"[OK] {self.name} capturou {count} links para '{kw}'.")
            except Exception as e:
                if "SOCKS" not in str(e): print(f"[!] Erro no {self.name} ({kw}): {e}")

class FeedEngine(BaseEngine):
    """Baixa listas massivas de links estáticos de repositórios OSINT"""
    def search(self, keywords):
        try:
            if isinstance(keywords, str): keywords = [keywords]
            jitter()
            r = requests.get(self.url, proxies=TOR_PROXIES, headers=get_random_headers(), timeout=45)
            if r.status_code == 200:
                import re
                content = r.text.lower()
                onions = list(set(re.findall(r'[a-z2-7]{56}\.onion|[a-z2-7]{16}\.onion', content)))
                found = 0
                for onion in onions:
                    url = f"http://{onion}/"
                    category = get_category(content, url)
                    if self.fetch_all:
                        self.results.append({'title': 'Massive Discovery', 'url': url, 'source': 'Feed', 'category': category})
                        found += 1
                    else:
                        for kw in keywords:
                            if kw.lower() in content or kw.lower() in onion:
                                self.results.append({'title': f'Match: {kw}', 'url': url, 'source': 'Feed', 'category': category})
                                found += 1
                                break
                if found: print(f"[OK] {self.name} extraiu {found} links.")
        except Exception as e:
            if "SOCKS" not in str(e): print(f"[!] Erro no Feed {self.name}: {e}")

class OnionSearchEngine(BaseEngine):
    """Buscador alternativo via Clearweb Mirror"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        for kw in keywords:
            try:
                jitter()
                search_url = f"https://onionsearch.org/search?q={kw}"
                r = requests.get(search_url, proxies=TOR_PROXIES, headers=get_random_headers(), timeout=45)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    f = 0
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if '.onion' in href and 'onionsearch.org' not in href:
                            title = a.text.strip()[:100]
                            category = get_category(title, href)
                            self.results.append({
                                'title': title, 
                                'url': href, 
                                'source': self.name,
                                'category': category
                            })
                            f += 1
                    if f: print(f"[OK] {self.name} capturou {f} links para '{kw}'.")
            except: pass

class DuckDuckGoEngine(BaseEngine):
    """Buscador DuckDuckGo Onion (Versão HTML)"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        for kw in keywords:
            try:
                jitter()
                params = {'q': kw, 'kl': 'wt-wt'}
                r = requests.get(self.url, params=params, proxies=TOR_PROXIES, headers=get_random_headers(), timeout=45)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    f = 0
                    for a in soup.find_all('a', class_='result__url', href=True):
                        href = a['href']
                        if '.onion' in href:
                            title = a.text.strip()[:100]
                            category = get_category(title, href)
                            self.results.append({
                                'title': title, 
                                'url': href, 
                                'source': self.name,
                                'category': category
                            })
                            f += 1
                    if f: print(f"[OK] {self.name} capturou {f} links para '{kw}'.")
            except: pass

class WikiSpider(BaseEngine):
    """Varre diretórios de links em busca de qualquer .onion que case com a keyword"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        try:
            jitter()
            r = requests.get(self.url, proxies=TOR_PROXIES, headers=get_random_headers(), timeout=45)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                f = 0
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    text = a.text.lower()
                    for kw in keywords:
                        if '.onion' in href and (kw.lower() in text or kw.lower() in href):
                            category = get_category(text, href)
                            self.results.append({
                                'title': a.text.strip()[:50], 
                                'url': href, 
                                'source': self.name,
                                'category': category
                            })
                            f += 1
                            break
                if f: print(f"[OK] {self.name} colheu {f} links.")
        except: pass

def save_results(results, filename="darkweb_leads_v5.csv"):
    if not results: return
    
    # Primeiro, carregamos o que já conhecemos de sessões passadas
    db = load_db()
    
    # Filtramos apenas o que é REALMENTE novo nesta sessão
    seen_in_this_session = set()
    truly_new_results = []
    
    for r in results:
        url = r['url']
        if url not in db and url not in seen_in_this_session:
            seen_in_this_session.add(url)
            truly_new_results.append(r)

    if not truly_new_results:
        print("\n[!] Nenhum link inédito encontrado nesta varredura.")
        return

    # Salvamos no Banco de Dados Persistente
    added_to_db = save_to_db(truly_new_results)

    # Salvamos no Arquivo CSV para entrega/análise
    keys = ['category', 'title', 'url', 'source', 'timestamp']
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        if f.tell() == 0: writer.writeheader()
        for res in truly_new_results:
            res['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow(res)
            
    print(f"\n[SUCESSO] {added_to_db} novos links INÉDITOS arquivados em {filename} e no banco de dados.")

def main():
    parser = argparse.ArgumentParser(description="Multi-Engine Massive OSINT Hunter (v6.0 - Protocolo Fantasma)")
    parser.add_argument("query", nargs='?', default="onion", help="Termo de busca (default: onion)")
    parser.add_argument("--all", action="store_true", help="Modo Infinito: Coleta todos os links independente da query")
    parser.add_argument("--search", action="store_true", help="Busca local na Base de Conhecimento (Offline)")
    args = parser.parse_args()

    if args.search:
        fts_search(args.query)
        sys.exit(0)

    # Inicia o Protocolo Fantasma renovando o circuito
    rotate_tor_circuit()

    # Expansão de keywords por sinônimos
    keywords = [args.query]
    if args.query.lower() in SYNONYMS:
        keywords.extend(SYNONYMS[args.query.lower()])
    
    mode_text = "[MODO INFINITO]" if args.all else f"para: {keywords}"
    print(f"🚀 Iniciando Busca Geração Máxima {mode_text}")
    
    engines = [
        AhmiaEngine('Ahmia_Onion', ENGINES['ahmia_onion'], args.all),
        AhmiaEngine('Ahmia_Clear', ENGINES['ahmia_clear'], args.all),
        DuckDuckGoEngine('DuckDuckGo_Onion', ENGINES['duckduckgo'], args.all),
        OnionSearchEngine('OnionSearch', None, args.all)
    ]
    
    for i, mirror in enumerate(ENGINES['hidden_wiki_mirrors']):
        engines.append(WikiSpider(f'Spider_{i+1}', mirror, args.all))
    
    # Adicionamos os Feeds Massivos (Static Lists)
    for i, feed_url in enumerate(FEEDS_URLS):
        engines.append(FeedEngine(f'Feed_{i+1}', feed_url, args.all))
    
    # Adicionamos o DeepCrawler para "Seeds" (Sementes) de alta densidade
    high_density_seeds = [
        'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otj3cy6ih7eypbad.onion/wiki/Main_Page',
        'http://torlinksge6enmcyy.onion/',
        'http://dirnxxdraygbifgc.onion/'
    ]
    for i, seed in enumerate(high_density_seeds):
        engines.append(DeepCrawler(f'DeepCrawler_{i+1}', seed, args.all))

    all_leads = []
    # Usamos 30 workers para o Modo Predator (Escala Máxima 5.0)
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(eng.search, keywords): eng for eng in engines}
        for future in as_completed(futures):
            eng = futures[future]
            if eng.results:
                print(f"[OK] {eng.name} coletou {len(eng.results)} novos links.")
                save_results(eng.results)

if __name__ == "__main__":
    main()
