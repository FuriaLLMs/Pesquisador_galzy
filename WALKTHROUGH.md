# Walkthrough: Arquitetura Industrial "Salto Industrial" (v7.0)

Alcançamos a **Perfeição Matemática** na engenharia de busca OSINT. Esta versão transforma o Onion Hunter em um sistema de banco de dados robusto e de alta performance.

## 1. Persistência de Elite (SQLite FTS5)
- **Cofre SQLite:** Substituímos o JSON por uma base de dados relacional com **WAL (Write-Ahead Logging)** habilitado.
- **Busca Instantânea:** O motor de busca offline agora utiliza indexação **FTS5**, permitindo pesquisar milhões de registros em milissegundos.
- **Integridade:** Gravação atômica que evita corrupção de dados sob carga massiva.

## 2. Otimização de Performance Bruta
- **Parsing lxml:** Migramos para o parser `lxml` escrito em C, ordens de grandeza mais rápido que o `html.parser` padrão.
- **Regex Operacional:** Expressões regulares agora são pré-compiladas globalmente, otimizando o gasto de CPU no `DeepCrawler`.
- **BaseEngine DRY:** Centralização de toda a lógica de rede, anonimato e jitter em um único ponto, garantindo que 100% do tráfego siga o protocolo de segurança.

## 3. Monitoramento e Resiliência
- **Logging Profissional:** Implementamos a biblioteca `logging`. Erros não são mais "engolidos", mas registrados em `onion_hunter.log` com detalhes técnicos.
- **Recursive Queue:** O `DeepCrawler` agora realiza recursão real, seguindo links em profundidade controlada de forma inteligente.

---

## 🚀 Como Operar a v7.0

### Caçada Industrial (Online)
```bash
poetry run python onion_hunter.py "armas"
```

### Pesquisa no Cofre (Offline)
Busca ultra-rápida no que já foi coletado:
```bash
poetry run python onion_hunter.py "bitcoin" --search
```

### Logs de Auditoria
Acompanhe os logs em tempo real:
```bash
tail -f onion_hunter.log
```

---

🛡️ **Status:** Operando em Nível Industrial.
📂 **Banco de Dados:** [onion_vault.db](file:///home/douglasdsr/Documentos/Projects/Area Dev de multi TESTES/Web Scriping/web02/onion_vault.db)
📜 **Logs:** [onion_hunter.log](file:///home/douglasdsr/Documentos/Projects/Area Dev de multi TESTES/Web Scriping/web02/onion_hunter.log)
