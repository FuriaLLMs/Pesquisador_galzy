# Escopo Legal e Metodológico: Projeto Onion Hunter Pro

## 1. Definição Formal do Objetivo
Construir um sistema automatizado para descoberta e categorização de serviços web publicamente acessíveis, não indexados por motores de busca tradicionais, operando estritamente dentro de limites legais e éticos.

## 2. Princípios Éticos de Operação
- **Transparência**: O User-Agent do crawler identificará claramente o projeto e fornecerá um meio de contato.
- **Respeito ao Servidor**: Implementação rigorosa de *Rate Limiting* para evitar sobrecarga (DoS não intencional) nos serviços alvo.
- **Conformidade com Robots.txt**: Obediência total às diretivas de exclusão de robôs.
- **Acesso Público**: A coleta limitará-se a dados disponíveis sem bypass de autenticação ou quebra de criptografia.

## 3. Conformidade Legal
- **LGPD/GDPR**: O sistema não coletará dados pessoais identificáveis (PII) de forma intencional. Caso detectados, serão descartados ou anonimizados na camada de Normalização.
- **Propriedade Intelectual**: O uso dos dados coletados será para fins de pesquisa, análise estatística e categorização semântica, respeitando os direitos autorais dos conteúdos.
- **Lei Carolina Dieckmann / CFAA**: O sistema não acessará áreas restritas ou protegidas por medidas de segurança.

## 4. Governança e Auditoria
- Todos os logs de acesso serão mantidos para auditoria.
- Política de retenção de dados: O conteúdo bruto será descartado após a extração dos metadados e embeddings, minimizando o risco de armazenamento de conteúdo sensível.
