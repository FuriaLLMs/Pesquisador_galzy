# Walkthrough: Arquitetura de Elite Dark Web (v6.0 - Protocolo Fantasma)

Elevamos a ferramenta ao padrão **industrial** de engenharia de busca e anonimato avançado.

## 1. Segurança e Anonimato Elite
- **Protocolo Fantasma (Circuit Rotation):** O script agora usa a biblioteca `stem` para rotacionar o circuito Tor (IP) automaticamente, tornando o rastreamento quase impossível.
- **Ofuscação Dinâmica:** Cada requisição utiliza um `User-Agent` diferente e introduz *jitter* (atrasos aleatórios) para simular o comportamento de um usuário real.
- **Isolamento Profissional:** O projeto agora utiliza **Poetry** para gerenciar dependências complexas e garantir um ambiente de execução imutável.

## 2. Motor de Busca de Segunda Geração
- **Busca Offline (FTS):** Você pode pesquisar em sua base de conhecimento local instantaneamente sem precisar se conectar à rede Tor.
- **Crawler Predator:** Descobre links recursivamente em profundidade.
- **Categorização Automática:** Classificação inteligente em Armamento, Financeiro, Narcóticos, etc.

## 3. Como Operar (Comandos v6.0)

### Varredura Global (Online)
Busca multi-idioma com rotação de IPs e ofuscação:
```bash
python3 onion_hunter.py "armas"
```

### Busca Local / Offline (FTS)
Pesquise no que já foi coletado sem usar internet:
```bash
python3 onion_hunter.py "termo" --search
```

## 4. Gerenciamento de Inteligência
- **[onion_knowledge_base.json](file:///home/douglasdsr/Documentos/Projects/Area Dev de multi TESTES/Web Scriping/web02/onion_knowledge_base.json):** Banco de dados estruturado com FTS.
- **[darkweb_leads_v5.csv](file:///home/douglasdsr/Documentos/Projects/Area Dev de multi TESTES/Web Scriping/web02/darkweb_leads_v5.csv):** Relatório de entrega categorizado.

🛡️ *Este é o estado da arte em descoberta OSINT na Dark Web.*
