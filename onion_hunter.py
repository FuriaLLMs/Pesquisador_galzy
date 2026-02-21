import requests
import sqlite3
import logging
import sys
import time
import argparse
import os
import random
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from stem import Signal
from stem.control import Controller
import threading
import queue

# --- Configuração de Logging Profissional (v7.0) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("onion_hunter.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("OnionHunter")

# --- Constantes de Engenharia de Busca (v7.0) ---
DB_FILE = "onion_vault.db"
ONION_REGEX = re.compile(r'[a-z2-7]{56}\.onion|[a-z2-7]{16}\.onion')
TOR_PROXIES = {
    'http': os.getenv('TOR_PROXY_HTTP', 'socks5h://127.0.0.1:9050'),
    'https': os.getenv('TOR_PROXY_HTTPS', 'socks5h://127.0.0.1:9050')
}
TOR_CONTROL_PORT = int(os.getenv('TOR_CONTROL_PORT', '9051'))
TIMEOUT_CONFIG = (15, 60) # (Connect, Read) - Aumentado para resiliência na Dark Web

class DatabaseManager:
    """Gerencia a persistência via SQLite FTS5 com Triggers Automáticos (Alta Fidelidade)"""
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL") 
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS onions (
                    url TEXT PRIMARY KEY,
                    title TEXT,
                    category TEXT,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            try:
                conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS fts_onions USING fts5(url, title, category, content='onions', content_rowid='rowid')")
                # TRIGGER: Sincronização automática O(1)
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS onions_ai AFTER INSERT ON onions BEGIN
                        INSERT INTO fts_onions(rowid, url, title, category) 
                        VALUES (new.rowid, new.url, new.title, new.category);
                    END;
                """)
            except sqlite3.OperationalError:
                logger.warning("FTS5 não disponível. Performance de busca reduzida.")

    def save_results(self, results):
        """Gravação em Lote (executemany) - Nível Sênior"""
        if not results: return 0
        added = 0
        data = [(r['url'], r['title'], r['category'], r['source']) for r in results]
        
        with self.lock:
            conn = self._get_conn()
            try:
                cursor = conn.executemany(
                    "INSERT OR IGNORE INTO onions (url, title, category, source) VALUES (?, ?, ?, ?)",
                    data
                )
                conn.commit()
                added = cursor.rowcount
            finally:
                conn.close()
        return added

    def search_local(self, query):
        """Busca O(log N) via MATCH do FTS5"""
        conn = self._get_conn()
        try:
            try:
                # MATCH é ordens de grandeza mais rápido que LIKE
                cursor = conn.execute(
                    "SELECT category, title, url, source FROM fts_onions WHERE fts_onions MATCH ? || '*' ORDER BY rank", 
                    (query,)
                )
                return cursor.fetchall()
            except sqlite3.OperationalError:
                q = f"%{query}%"
                cursor = conn.execute(
                    "SELECT category, title, url, source FROM onions WHERE title LIKE ? OR url LIKE ?", 
                    (q, q)
                )
                return cursor.fetchall()
        finally:
            conn.close()

db = DatabaseManager()

def rotate_tor_circuit():
    """Tenta renovar o IP do Tor via Controller"""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as ctrl:
            ctrl.authenticate()
            ctrl.signal(Signal.NEWNYM)
            logger.info("Circuito Tor renovado com sucesso (Novo IP solicitado).")
    except Exception as e:
        logger.debug(f"Não foi possível renovar o circuito Tor: {e}")

def get_random_headers():
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0'
    ]
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

def jitter():
    time.sleep(random.uniform(1.0, 3.5))

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

    def _fetch(self, url, params=None):
        """Método Centralizado de Busca (DRY & Seguro)"""
        try:
            jitter()
            r = requests.get(
                url, 
                params=params, 
                proxies=TOR_PROXIES, 
                headers=get_random_headers(), 
                timeout=TIMEOUT_CONFIG
            )
            r.raise_for_status()
            return r.text
        except requests.exceptions.RequestException as e:
            logger.debug(f"Falha na rede Tor para {self.name} ({url}): {e}")
            return None

    def search(self, query):
        raise NotImplementedError

class DeepCrawler(BaseEngine):
    """Spider que descobre novos links e os emite para a pool sem sequestrar threads"""
    def __init__(self, name, url, fetch_all=False, max_depth=1, current_depth=0, visited=None):
        super().__init__(name, url, fetch_all)
        self.max_depth = max_depth
        self.current_depth = current_depth
        self.visited = visited if visited is not None else set()

    def search(self, keywords):
        if self.url in self.visited or self.current_depth > self.max_depth:
            return
        
        self.visited.add(self.url)
        content = self._fetch(self.url)
        if not content:
            return

        content_lower = content.lower()
        onions = list(set(ONION_REGEX.findall(content_lower)))
        
        for onion in onions:
            onion_url = f"http://{onion}/"
            category = get_category(content_lower, onion_url)
            
            match = False
            if self.fetch_all:
                match = True
            else:
                for kw in keywords:
                    if kw.lower() in content_lower or kw.lower() in onion:
                        match = True
                        break
            
            if match:
                yield {
                    'title': f'Deep Discovery (D{self.current_depth})', 
                    'url': onion_url, 
                    'source': self.name, 
                    'category': category,
                    'is_crawler': True,
                    'depth': self.current_depth + 1
                }

class AhmiaEngine(BaseEngine):
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        for kw in keywords:
            html = self._fetch(self.url, params={'q': kw})
            if html:
                soup = BeautifulSoup(html, 'lxml')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.onion' in href and 'ahmia.fi' not in href:
                        url = href.split('search_result=')[-1].split('&')[0] if 'redirect' in href else href
                        url = url.replace('%3A', ':').replace('%2F', '/')
                        if '.onion' in url and 'juhanurmi' not in url:
                            title = a.text.strip() or f"Match: {kw}"
                            category = get_category(title, url)
                            yield {
                                'title': title[:100], 
                                'url': url, 
                                'source': self.name,
                                'category': category
                            }

class FeedEngine(BaseEngine):
    """Baixa listas massivas de links estáticos de repositórios OSINT"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        content = self._fetch(self.url)
        if content:
            content_lower = content.lower()
            onions = list(set(ONION_REGEX.findall(content_lower)))
            for onion in onions:
                url = f"http://{onion}/"
                category = get_category(content_lower, url)
                
                match = False
                if self.fetch_all:
                    match = True
                else:
                    for kw in keywords:
                        if kw.lower() in content_lower or kw.lower() in onion:
                            match = True
                            break
                
                if match:
                    yield {'title': 'Massive Discovery', 'url': url, 'source': 'Feed', 'category': category}

class OnionSearchEngine(BaseEngine):
    """Buscador alternativo via Clearweb Mirror"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        for kw in keywords:
            search_url = f"https://onionsearch.org/search?q={kw}"
            html = self._fetch(search_url)
            if html:
                soup = BeautifulSoup(html, 'lxml')
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '.onion' in href and 'onionsearch.org' not in href:
                        title = a.text.strip()[:100]
                        category = get_category(title, href)
                        yield {
                            'title': title, 
                            'url': href, 
                            'source': self.name,
                            'category': category
                        }

class DuckDuckGoEngine(BaseEngine):
    """Buscador DuckDuckGo Onion (Versão HTML)"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        for kw in keywords:
            html = self._fetch(self.url, params={'q': kw, 'kl': 'wt-wt'})
            if html:
                soup = BeautifulSoup(html, 'lxml')
                for a in soup.find_all('a', class_='result__url', href=True):
                    href = a['href']
                    if '.onion' in href:
                        title = a.text.strip()[:100]
                        category = get_category(title, href)
                        yield {'title': title, 'url': href, 'source': self.name, 'category': category}

class WikiSpider(BaseEngine):
    """Varre diretórios de links buscando correspondências"""
    def search(self, keywords):
        if isinstance(keywords, str): keywords = [keywords]
        html = self._fetch(self.url)
        if html:
            soup = BeautifulSoup(html, 'lxml')
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.text.lower()
                for kw in keywords:
                    if '.onion' in href and (kw.lower() in text or kw.lower() in href):
                        category = get_category(text, href)
                        yield {
                            'title': a.text.strip()[:50], 
                            'url': href, 
                            'source': self.name,
                            'category': category
                        }
                        break

def save_results(results, filename="darkweb_leads_v8.csv"):
    """Salva resultados no cofre SQLite (Batch) e no CSV de Auditoria"""
    if not results: return
    
    added_to_db = db.save_results(results)

    if added_to_db > 0:
        import csv
        keys = ['category', 'title', 'url', 'source', 'timestamp']
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            if f.tell() == 0: writer.writeheader()
            for res in results:
                res['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                # Filtramos chaves extras para o CSV
                row = {k: res.get(k, '') for k in keys}
                writer.writerow(row)
        
        logger.info(f"Sucesso: {added_to_db} novos registros no cofre e em {filename}.")

def main():
    parser = argparse.ArgumentParser(description="Multi-Engine Massive OSINT Hunter (v8.0 - Perfeição Matemática)")
    parser.add_argument("query", nargs='?', default="onion", help="Termo de busca (default: onion)")
    parser.add_argument("--all", action="store_true", help="Modo Infinito")
    parser.add_argument("--search", action="store_true", help="Busca local FTS5 (MATCH)")
    parser.add_argument("--depth", type=int, default=1, help="Profundidade do Crawler (default: 1)")
    args = parser.parse_args()

    if args.search:
        results = db.search_local(args.query)
        if results:
            logger.info(f"FTS Store: {len(results)} resultados para '{args.query}':")
            for r in results:
                print(f"[{r[0]}] {r[1]} | {r[2]}")
        else:
            logger.info(f"Cofre: Nenhum resultado para '{args.query}'.")
        sys.exit(0)

    rotate_tor_circuit()

    keywords = [args.query]
    if args.query.lower() in SYNONYMS:
        keywords.extend(SYNONYMS[args.query.lower()])
    
    logger.info(f"🚀 Modo Predator v8.0 iniciado para: {keywords if not args.all else 'Global'}")
    
    # Pool de Execução Sênior (30 Workers)
    executor = ThreadPoolExecutor(max_workers=30)
    visited = set() # Controle de redundância global
    tasks = []
    
    # Inicialização dos Motores
    initial_engines = [
        AhmiaEngine('Ahmia_Onion', ENGINES['ahmia_onion'], args.all),
        AhmiaEngine('Ahmia_Clear', ENGINES['ahmia_clear'], args.all),
        DuckDuckGoEngine('DuckDuckGo_Onion', ENGINES['duckduckgo'], args.all),
        OnionSearchEngine('OnionSearch', None, args.all)
    ]
    for i, mirror in enumerate(ENGINES['hidden_wiki_mirrors']):
        initial_engines.append(WikiSpider(f'Spider_{i+1}', mirror, args.all))
    for i, feed in enumerate(FEEDS_URLS):
        initial_engines.append(FeedEngine(f'Feed_{i+1}', feed, args.all))

    # Sementes (Seeds) de Alta Densidade
    seeds = [
        'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otj3cy6ih7eypbad.onion/wiki/Main_Page',
        'http://torlinksge6enmcyy.onion/',
        'http://dirnxxdraygbifgc.onion/'
    ]
    for i, seed in enumerate(seeds):
        initial_engines.append(DeepCrawler(f'CrawlerSeed_{i+1}', seed, args.all, max_depth=args.depth, visited=visited))

    # Task Submission Loop
    tasks = []
    for eng in initial_engines:
        tasks.append(executor.submit(lambda e=eng: list(e.search(keywords))))

    batch_buffer = []
    try:
        while tasks:
            # Iteramos em uma cópia para poder adicionar novas tasks dinamicamente
            current_tasks = list(tasks)
            remaining_tasks = []
            
            for t in current_tasks:
                if t.done():
                    try:
                        results = t.result()
                        if results:
                            batch_buffer.extend(results)
                            
                            # Task Feedback Loop: Processa novas descobertas para recursão
                            for res in results:
                                if res.get('is_crawler') and res['depth'] <= args.depth:
                                    new_crawler = DeepCrawler(
                                        f"SubSpy_{res['depth']}", 
                                        res['url'], 
                                        args.all, 
                                        max_depth=args.depth, 
                                        current_depth=res['depth'],
                                        visited=visited
                                    )
                                    tasks.append(executor.submit(lambda e=new_crawler: list(e.search(keywords))))
                                    logger.info(f"[FEEDBACK] Novo alvo: {res['url'][:30]}... (D{res['depth']})")

                            if len(batch_buffer) >= 20:
                                save_results(batch_buffer)
                                batch_buffer = []
                    except Exception as e:
                        logger.debug(f"Task finalizada com erro: {e}")
                else:
                    remaining_tasks.append(t)
            
            tasks = remaining_tasks
            if not tasks: break
            time.sleep(0.5)

        # Flush final do buffer
        if batch_buffer:
            save_results(batch_buffer)

    except KeyboardInterrupt:
        logger.info("Encerrando caçada por comando do usuário...")
    finally:
        executor.shutdown(wait=False)
        logger.info("Operação v8.0 finalizada. Cofre sincronizado.")

if __name__ == "__main__":
    main()
