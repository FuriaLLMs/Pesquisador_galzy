# Walkthrough: Arquitetura Sênior "Geração Predator" (v8.0)

Alcançamos o ápice da engenharia de busca para a Dark Web. A versão 8.0 abandona as limitações de protótipos e adota padrões de design de nível sênior para performance industrial.

## 1. Otimização de Persistência (O(log N))
- **SQLite Triggers:** A tabela FTS5 agora se atualiza automaticamente via gatilhos `AFTER INSERT`. Eliminamos a reconstrução dispendiosa do índice, garantindo que o cofre permaneça rápido mesmo com milhões de registros.
- **Operador MATCH & Prefix Match:** As buscas locais agora são baseadas em tokens (B-Trees). Implementamos suporte automático a prefixos (`link*`), permitindo resultados instantâneos e precisos.
- **Batch Saving (executemany):** Os resultados são acumulados em memória e gravados em lote, otimizando transações de IO e reduzindo o desgaste do disco.

## 2. Eficiência Bruta de Memória (Zero RAM Bloat)
- **Padrão Generator (Yield):** Todos os motores (Ahmia, DuckDuckGo, Feeds) foram refatorados para emitir links individualmente. Isso permite que o script processe manifestos gigantescos (como feeds de 200MB) mantendo o consumo de memória estável e baixo.

## 3. Concorrência "Predator" (Task Feedback Loop)
- **Desacoplamento de Threads:** O `DeepCrawler` não sequestra mais threads na recursão. Quando um novo link é descoberto, ele é devolvido ao loop principal (`main`), que agenda uma nova tarefa na pool de forma assíncrona.
- **Recursão Dinâmica:** O sistema se expande organicamente conforme descobre novos alvos, sem risco de estourar a pilha de recursão ou bloquear a pool de execução.

---

## 🚀 Guia de Operação v8.0

### Caçada de Elite (Online)
```bash
# Busca recursiva (Depth 1) com modo Predator
poetry run python onion_hunter.py "alvo" --depth 1
```

### Busca Instantânea no Cofre (Offline)
Utiliza o poder do FTS5:
```bash
poetry run python onion_hunter.py "bitcoin" --search
```

### Monitoramento Industrial
```bash
tail -f onion_hunter.log
```

---

🛡️ **Status:** Perfeição Matemática Alcançada.
📂 **Vault:** [onion_vault.db](file:///home/douglasdsr/Documentos/Projects/Area Dev de multi TESTES/Web Scriping/web02/onion_vault.db)
📜 **Logs:** [onion_hunter.log](file:///home/douglasdsr/Documentos/Projects/Area Dev de multi TESTES/Web Scriping/web02/onion_hunter.log)
