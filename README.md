# 🕵️‍♂️ Pesquisador Galzy v6.0 (Onion Hunter)

> **"Transformando o obscuro em algo visível e claro."**

O **Pesquisador Galzy** é um motor de busca massivo e automatizado para a Dark Web (Rede Tor), projetado para operações de **OSINT (Open-Source Intelligence)** de alta performance. Esta ferramenta descobre, categoriza e cataloga endereços `.onion` em escala industrial, utilizando uma arquitetura de "Elite" focada em anonimato e inteligência cumulativa.

---

## 🚀 Principais Funcionalidades

### 🌐 Modo Babel (Busca Global)
Não se limite ao inglês. O motor traduz automaticamente seus termos de busca para:
*   **Russo** (оружие)
*   **Chinês** (武器)
*   **Árabe** (أسلحة)
*   **Francês** (armes)
*   **Espanhol** (armas)
*   *E muitos outros jargões técnicos.*

### 👻 Protocolo Fantasma (Advanced Anonymity)
Anonimato de nível industrial integrado:
*   **Circuit Rotation:** Rotação automática de circuitos Tor (IP) via `stem`.
*   **Dynamic Fingerprinting:** Rotação aleatória de `User-Agents` em cada requisição.
*   **Traffic Obfuscation:** Controle de *jitter* (atrasos aleatórios) para simular comportamento humano.

### 🧠 Inteligência Cumulativa (Modo Arquivista)
*   **Persistent Knowledge Base:** Banco de dados JSON que aprende a cada execução e evita duplicidade.
*   **Full-Text Search (FTS):** Motor de busca local para consultar o que já foi coletado **offline** e de forma instantânea.
*   **Categorização Automática:** Classificação inteligente de links em tags como `Armamento`, `Financeiro`, `Narcóticos`, `Fóruns`, etc.

---

## 🛠️ Stack Técnica
*   **Linguagem:** Python 3.14+
*   **Gerenciador de Dependências:** Poetry
*   **Conectividade:** Tor Network (Socks5h)
*   **Bibliotecas Chave:** `requests`, `bs4`, `stem`, `colorama`.

---

## 🔧 Instalação e Configuração

### 1. Requisitos Prévios
Certifique-se de ter o **Tor Service** rodando com as portas padrão:
*   SocksPort: `9050`
*   ControlPort: `9051` (Necessário para a rotação de circuitos IPs)

### 2. Clonar e Instalar
```bash
git clone https://github.com/FuriaLLMs/Pesquisador_galzy.git
cd Pesquisador_galzy
poetry install
```

---

## 📖 Como Usar

### 🕵️ Varredura Global de Inteligência
Realiza busca multi-idioma com todo o protocolo de anonimato:
```bash
poetry run python onion_hunter.py "armas"
```

### 🚀 Extração Massiva (Infinito)
Coleta tudo o que as sementes e feeds mundiais oferecerem:
```bash
poetry run python onion_hunter.py --all
```

### 📂 Busca Offline (Full-Text Search)
Pesquise na sua base de conhecimento local sem internet:
```bash
poetry run python onion_hunter.py "termo" --search
```

---

## 🛡️ Segurança e Ética
Esta ferramenta foi criada estritamente para fins de pesquisa **OSINT e Ética**. O autor não se responsabiliza pelo uso indevido. Mantenha seu ambiente de execução isolado (recomendado: Whonix ou Tails).

---

## ✍️ Desenvolvedor
Criado com ❤️ por **Douglas Scarello** para a **FuriaLLMs**.
