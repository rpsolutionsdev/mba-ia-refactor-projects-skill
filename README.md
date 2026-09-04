# Skill de Auditoria e Refatoração Arquitetural (`/refactor-arch`)

Implementação de **Custom Skill agnóstica de tecnologia** para auditoria automatizada e refatoração arquitetural para o padrão **MVC (Model-View-Controller)** com validação de runtime em 3 projetos legados.

---

## 📑 Sumário Executivo
* [1. Análise Manual](#1-análise-manual)
* [2. Construção da Skill](#2-construção-da-skill)
* [3. Resultados](#3-resultados)
* [4. Como Executar](#4-como-executar)
* [5. Estrutura do Repositório](#5-estrutura-do-repositório)

---

## 1. Análise Manual

Mapeamento prévio dos problemas arquiteturais, falhas de segurança e code smells nos 3 projetos-alvo.

### 📦 Projeto 1: `code-smells-project` (Python / Flask 3.1.1 — E-commerce API)

| Severidade | Anti-pattern / Problema | Localização | Relevância / Impacto |
| :--- | :--- | :--- | :--- |
| 🔴 **CRITICAL** | **SQL Injection via Concatenação** | `models.py:28, 48, 58, 68, 109, 140, 280, 291` | Interpolação direta de inputs em queries; permite extração e destruição total do banco. |
| 🔴 **CRITICAL** | **Hardcoded Secrets & Leaks** | `app.py:7`, `controllers.py:289` | `SECRET_KEY` exposta no código e vazada publicamente na resposta do `/health`. |
| 🔴 **CRITICAL** | **Endpoints Perigosos sem Autenticação** | `app.py:47-79` | `/admin/query` e `/admin/reset-db` permitem execução SQL arbitrária sem auth. |
| 🔴 **CRITICAL** | **Senhas em Plaintext** | `models.py:83, 99, 110, 127` | Credenciais armazenadas e validadas sem hash criptográfico. |
| 🟠 **HIGH** | **God File / Falta de Separação** | `models.py:1-315` | Arquivo único com regras, SQL e formatação de 4 domínios distintos. |
| 🟡 **MEDIUM** | **Consultas N+1** | `models.py:187-199, 219-231` | Queries em loop para itens e nomes de produtos; degradação severa com escala. |
| 🟢 **LOW** | **Magic Numbers & Logs com `print`** | `models.py:257-263`, `controllers.py:8, 57` | Regras de desconto com literais soltos e ausência de logger estruturado. |

### 📦 Projeto 2: `ecommerce-api-legacy` (Node.js / Express — LMS API com Checkout)

| Severidade | Anti-pattern / Problema | Localização | Relevância / Impacto |
| :--- | :--- | :--- | :--- |
| 🔴 **CRITICAL** | **Exposição de Secrets & Gateway Key** | `src/utils.js:1-7`, `src/AppManager.js:45` | Credenciais de banco, SMTP e gateway live no código; log de cartão de crédito no console. |
| 🔴 **CRITICAL** | **Criptografia Falsa (*Bad Crypto*)** | `src/utils.js:17-23` | Fatias repetidas de base64 sem salt; hashes trivialmente reversíveis. |
| 🟠 **HIGH** | **God Class (*AppManager*) & Callback Hell** | `src/AppManager.js:4-139` | Classe única acumulando DDL, rotas, pagamentos e até 5 níveis de callbacks. |
| 🟠 **HIGH** | **Estado Global Mutável** | `src/utils.js:9-10`, `src/AppManager.js:59` | `globalCache` e `totalRevenue` em memória; gera race conditions em concorrência. |
| 🟡 **MEDIUM** | **N+1 Query Pyramid no Relatório** | `src/AppManager.js:83-128` | 4 loops assíncronos aninhados gerando I/O excessivo. |
| 🟢 **LOW** | **Nomenclatura Críptica** | `src/AppManager.js:29-33` | Variáveis de 1 caractere (`u`, `e`, `p`, `cid`, `cc`) prejudicando legibilidade. |

### 📦 Projeto 3: `task-manager-api` (Python / Flask — Task Manager API)

| Severidade | Anti-pattern / Problema | Localização | Relevância / Impacto |
| :--- | :--- | :--- | :--- |
| 🔴 **CRITICAL** | **Vazamento de Hash de Senha na API** | `models/user.py:21`, `routes/user_routes.py:40, 85` | `User.to_dict()` inclui `'password': self.password`, expondo hashes em endpoints públicos. |
| 🔴 **CRITICAL** | **Criptografia Insegura (MD5 sem Salt)** | `models/user.py:29, 32` | Hashing com MD5 vulnerável a rainbow tables e ataques de força bruta. |
| 🟠 **HIGH** | **Fat Routes & Lógica no Controlador** | `routes/report_routes.py:13-100`, `routes/task_routes.py:12-63` | Rotas com agregações analíticas e regras de negócio sem delegação a Services. |
| 🟠 **HIGH** | **Credenciais SMTP Hardcoded** | `services/notification_service.py:9-10` | E-mail e senha corporativa (`senha123`) fixadas no código. |
| 🟡 **MEDIUM** | **Consultas N+1** | `routes/report_routes.py:53-68`, `routes/task_routes.py:41-58` | Queries individuais por usuário e categoria dentro de loops de listagem. |
| 🟡 **MEDIUM** | **Tratamento de Exceções Vazio (*Bare Excepts*)** | `routes/task_routes.py:62, 236`, `routes/report_routes.py:186` | Blocos `except:` sem tipo capturado, mascarando bugs de runtime. |
| 🟢 **LOW** | **APIs Deprecated (`datetime.utcnow()`)** | `models/task.py:15-16`, `routes/task_routes.py:31` | Método obsoleto no Python 3.12+; risco de quebra em versões futuras. |

---

## 2. Construção da Skill

### 🧠 Decisões de Design
A Skill foi estruturada modularmente sob `.claude/skills/refactor-arch/`:
* **`SKILL.md`**: Prompt operacional que orquestra o ciclo em 3 fases sequenciais e impõe confirmação humana `[y/n]` antes de qualquer mutação de código.
* **`analysis-heuristics.md`**: Heurísticas agnósticas de detecção de linguagem, framework, banco de dados e topologia.
* **`anti-patterns-catalog.md`**: Catálogo estruturado de 14 anti-patterns com severidades (`CRITICAL` a `LOW`) e detecção de APIs obsoletas.
* **`report-template.md`**: Template padronizado para o relatório da Fase 2.
* **`mvc-guidelines.md`**: Definição formal das responsabilidades de cada camada (`config`, `models`, `views/routes`, `controllers`, `services`, `middlewares`, limpeza física de código legado e política de hashing seguro).
* **`refactoring-playbook.md`**: 9 padrões de transformação com exemplos práticos de código Antes / Depois (incluindo hashing estrito sem fallbacks e remoção de código legado substituído).

### 🎯 Agnosticismo de Tecnologia
* **Inspeção Dinâmica de Manifestos**: Identifica dependências e runtimes sem premissas fixas.
* **Princípios Universais de Engenharia**: Avalia coesão, acoplamento, SOLID e OWASP independentemente de linguagem.
* **Estrutura Padrão Universal**: Unifica a entrega no layout desacoplado `src/` com camadas de domínio claras.

### ⚠️ Desafios Encontrados & Soluções
* **Contratos de API Legados**: Garantida 100% de compatibilidade nos schemas de request/response após refatoração.
* **Integridade Referencial**: Implementação de `PRAGMA foreign_keys = ON` e exclusão em cascata transacional no Node.js.
* **Proteção de Credenciais e Hashing Estrito**: Substituição de plaintext e MD5 por hashes com PBKDF2/scrypt com salt, eliminando categoricamente qualquer fallback para hashes inseguros.
* **Purga de Artefatos Legados**: Remoção física e integral de todos os arquivos e pastas substituídos, impedindo que vulnerabilidades auditadas residam paralelamente no repositório.

---

## 3. Resultados

### 📊 Resumo dos Relatórios de Auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total Findings | Relatório |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`code-smells-project`** | Python + Flask | 4 | 2 | 2 | 2 | **10** | [`audit-project-1.md`](reports/audit-project-1.md) |
| **`ecommerce-api-legacy`** | Node.js + Express | 2 | 3 | 2 | 1 | **8** | [`audit-project-2.md`](reports/audit-project-2.md) |
| **`task-manager-api`** | Python + Flask | 2 | 2 | 2 | 1 | **7** | [`audit-project-3.md`](reports/audit-project-3.md) |

---

### 🔄 Comparativo Estrutural Antes / Depois

| Projeto | Estrutura Antes (Legada) | Estrutura Depois (MVC Refatorada) |
| :--- | :--- | :--- |
| **`code-smells-project`** | Monolítica em 4 arquivos (`app.py`, `models.py`, `controllers.py`, `database.py`) com SQL Injection e God File. | `src/config/`, `src/models/`, `src/routes/`, `src/controllers/`, `src/middlewares/`, `app.py` com queries parametrizadas e arquivos legados purgados. |
| **`ecommerce-api-legacy`** | `AppManager.js` único com DDL, rotas, pagamentos e callback hell. | `src/config/`, `src/models/`, `src/routes/`, `src/controllers/`, `src/services/`, `src/middlewares/` com async/await e `AppManager.js`/`utils.js` removidos. |
| **`task-manager-api`** | Parcialmente dividida mas com Fat Routes, MD5 e vazamento de senhas. | `src/config/`, `src/models/`, `src/routes/`, `src/controllers/`, `src/services/` com timezone-aware, PBKDF2 estrito e pastas legadas deletadas. |

---

### ✅ Checklist de Validação (3/3 Projetos)

* **Fase 1 — Análise**:
  - [x] Linguagem e Framework detectados corretamente (Python/Flask e Node.js/Express)
  - [x] Domínio descrito com precisão (E-commerce, LMS, Task Manager)
  - [x] Contagem de arquivos condizente com a realidade
* **Fase 2 — Auditoria**:
  - [x] Relatório estruturado seguindo o template oficial
  - [x] Arquivo e linhas exatas em cada finding
  - [x] Ordenação rigorosa por severidade (`CRITICAL` → `LOW`)
  - [x] Mínimo de 5 findings identificados por projeto (10, 8 e 7)
  - [x] Detecção de APIs obsoletas (`datetime.utcnow`, MD5)
  - [x] Pausa obrigatória para confirmação `[y/n]`
* **Fase 3 — Refatoração**:
  - [x] Estrutura modular em camadas MVC sob `src/`
  - [x] Configuração centralizada via variáveis de ambiente
  - [x] Models parametrizados, controllers finos e rotas desacopladas
  - [x] Error handling global e centralizado
  - [x] Exclusão física definitiva de arquivos e pastas legadas substituídas
  - [x] Zero fallbacks/caminhos alternativos para senhas em texto puro ou algoritmos fracos (MD5)
  - [x] Aplicações inicializam sem erros e todos os endpoints respondem com sucesso

---

### 📋 Logs de Validação dos Endpoints

* **Projeto 1 (`code-smells-project`)**:
  ```
  [OK] [GET /health] OK - Sem vazamento de secret
  [OK] [GET /] OK
  [OK] [GET /produtos] OK - 10 produtos retornados
  [OK] [GET /produtos/busca] OK - 3 itens encontrados
  [OK] [POST /produtos] OK - Criado produto ID 11
  [OK] [POST /login] OK - Autenticação com senha hash validada
  [OK] [POST /pedidos] OK - Pedido criado com cálculo correto
  [OK] [GET /relatorios/vendas] OK - Relatório gerado com sucesso
  ```

* **Projeto 2 (`ecommerce-api-legacy`)**:
  ```
  [OK] [POST /api/checkout] Sucesso: enrollment_id=2
  [OK] [POST /api/checkout] Recusado: status 400 correto
  [OK] [GET /api/admin/financial-report] Sucesso: 2 cursos listados
  [OK] [DELETE /api/users/1] Sucesso: Usuário e matrículas deletados
  ```

* **Projeto 3 (`task-manager-api`)**:
  ```
  [OK] [GET /health] OK
  [OK] [POST /categories] Categoria criada ID 1
  [OK] [POST /users] Usuário criado ID 1 - Hash omitido com segurança
  [OK] [POST /login] Autenticação com PBKDF2 realizada com sucesso
  [OK] [POST /tasks] Task criada ID 1
  [OK] [GET /tasks] Tarefas listadas (sem queries N+1)
  [OK] [GET /reports/summary] Relatório geral OK
  [OK] [GET /reports/user/1] Relatório por usuário OK
  ```

---

### 🌐 Comportamento em Stacks Diferentes
* **Python / Flask**: A skill modularizou monolitos planos e projetos semi-organizados, substituindo SQL Injection por prepared statements e MD5 por hashes padrão de mercado.
* **Node.js / Express**: A skill desfez o acoplamento de classes *God Manager*, eliminou o *Callback Hell* através de Promises nativas e garantiu integridade referencial via SQLite foreign keys.

---

## 4. Como Executar

### Pré-requisitos
* Python 3.10+ (`flask`, `flask-cors`, `flask-sqlalchemy`, `werkzeug`)
* Node.js 18+ e npm
* CLI compatível com Custom Skills (Claude Code, Gemini CLI ou Antigravity CLI)

### Comandos de Execução e Teste

```bash
# Projeto 1 — Python / Flask
cd code-smells-project
claude "/refactor-arch"
py verify_api.py

# Projeto 2 — Node.js / Express
cd ../ecommerce-api-legacy
claude "/refactor-arch"
node verify_api.js

# Projeto 3 — Python / Flask
cd ../task-manager-api
claude "/refactor-arch"
py verify_api.py
```

---

## 5. Estrutura do Repositório

```
mba-ia-refactor-projects-skill/
├── README.md                              # Documentação consolidada (Smart Brevity)
├── reports/                               # Relatórios de auditoria da Fase 2
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
├── code-smells-project/                   # Projeto 1 (Python / Flask)
│   ├── .claude/skills/refactor-arch/      # Skill e referências Markdown
│   ├── src/                               # Código refatorado MVC
│   ├── app.py & verify_api.py
├── ecommerce-api-legacy/                  # Projeto 2 (Node.js / Express)
│   ├── .claude/skills/refactor-arch/      # Skill e referências Markdown
│   ├── src/                               # Código refatorado MVC
│   ├── api.http & verify_api.js
└── task-manager-api/                      # Projeto 3 (Python / Flask)
    ├── .claude/skills/refactor-arch/      # Skill e referências Markdown
    ├── src/                               # Código refatorado MVC
    └── app.py & verify_api.py
```