================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~200 lines of code

## Summary
CRITICAL: 2 | HIGH: 3 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] Exposição de Credenciais e Chaves de Gateway no Código
File: src/utils.js:1-7, src/AppManager.js:45
Description: Objeto `config` contém credenciais de banco, e-mail SMTP e chave ativa de gateway de pagamento (`pk_live_1234567890abcdef`) hardcoded, além de logar dados de cartão de crédito e chaves confidenciais no console.
Impact: Risco crítico de segurança e vazamento de dados de pagamento sensíveis em logs públicos e repositórios.
Recommendation: Migrar todas as configurações para variáveis de ambiente com `process.env` e mascarar dados de cartão em logs.

### [CRITICAL] Criptografia Falsa e Insegura (Bad Crypto)
File: src/utils.js:17-23
Description: A função `badCrypto` gera hashes previsíveis concatenando pedaços repetidos de base64 (`Buffer.from(pwd).toString('base64').substring(0, 2)`), sem salt e sem algoritmo criptográfico real.
Impact: As senhas dos usuários podem ser facilmente quebradas ou adivinhadas por qualquer agente mal-intencionado.
Recommendation: Substituir por biblioteca criptográfica moderna como `bcryptjs` ou `crypto.scryptSync` com salt único por usuário.

### [HIGH] God Class (AppManager) & Violação Total de MVC
File: src/AppManager.js:4-139
Description: A classe `AppManager` atua como uma *God Class*, acumulando criação de tabelas SQLite DDL, inserção de seeds, roteamento HTTP, regras de pagamento e geração de relatórios no mesmo arquivo.
Impact: Acoplamento extremo, código impossível de testar com testes unitários e dificuldade para escalar novas funcionalidades.
Recommendation: Decompor o `AppManager` em camadas MVC (`src/config/`, `src/models/`, `src/controllers/`, `src/services/`, `src/routes/`).

### [HIGH] Callback Hell & Pyramid of Doom em Operações Assíncronas
File: src/AppManager.js:37-77, 83-128
Description: Aninhamento de 4 a 5 níveis de callbacks do driver `sqlite3` (`db.get` -> `db.get` -> `db.run` -> `db.run`), tornando o código ilegível e propenso a falhas de fluxo.
Impact: Dificuldade extrema de manutenção, propensão a unhandled promise rejections e tratamento de erros fragmentado.
Recommendation: Utilizar Promises e funções assíncronas com `async/await` e blocos estruturados de captura de erro.

### [HIGH] Estado Global Mutável em Memória (Global Mutable State)
File: src/utils.js:9-10, src/AppManager.js:59
Description: As variáveis `globalCache` e `totalRevenue` vivem no escopo global do módulo Node.js, sendo alteradas a cada requisição HTTP sem controle transacional.
Impact: Condições de corrida (*race conditions*), inconsistência de dados em ambientes concorrentes e vazamento de memória.
Recommendation: Encapsular cache em um serviço dedicado ou persistir métricas financeiras diretamente no banco de dados.

### [MEDIUM] Consulta N+1 no Relatório Financeiro
File: src/AppManager.js:83-128
Description: O relatório financeiro faz uma busca por cursos e depois dispara queries assíncronas aninhadas em loops `forEach` para matrículas, usuários e pagamentos.
Impact: Gargalo crítico de I/O de banco de dados conforme o volume de alunos e cursos cresce.
Recommendation: Substituir a pirâmide de loops por uma query SQL agregada com `LEFT JOIN` e `SUM(payments.amount)`.

### [MEDIUM] Exclusão sem Cascata e Integridade Referencial Quebrada
File: src/AppManager.js:131-137
Description: Rota `DELETE /api/users/:id` remove o usuário diretamente do banco deixando matrículas (`enrollments`) e pagamentos (`payments`) órfãos sem tratamento de chave estrangeira.
Impact: Corrupção da base relacional e erros ao calcular relatórios e históricos de transações.
Recommendation: Habilitar `PRAGMA foreign_keys = ON` e aplicar exclusão em cascata ou remoção transacional de dependências.

### [LOW] Nomenclatura Críptica e Variáveis de Caractere Único
File: src/AppManager.js:29-33
Description: Uso de variáveis abreviadas e confusas (`u`, `e`, `p`, `cid`, `cc`) para extrair campos da requisição.
Impact: Prejudica a legibilidade e entendimento do fluxo de negócio.
Recommendation: Utilizar desestruturação semântica com nomes descritivos (`username`, `email`, `password`, `courseId`, `cardNumber`).

================================
Total: 8 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
