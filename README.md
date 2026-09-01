# Desafio: Skill de Auditoria e Refatoração Arquitetural (`/refactor-arch`)

Repositório contendo a implementação da **Custom Skill de Auditoria e Refatoração Arquitetural para MVC**, seus arquivos de referência agnósticos de tecnologia, relatórios de auditoria gerados e o código refatorado e validado dos 3 projetos legados.

---

## 📑 Sumário

1. [Análise Manual dos Projetos](#1-análise-manual-dos-projetos)
2. [Construção da Skill](#2-construção-da-skill)
3. [Resultados e Validação](#3-resultados-e-validação)
4. [Como Executar](#4-como-executar)
5. [Estrutura do Repositório](#5-estrutura-do-repositório)

---

## 1. Análise Manual dos Projetos

Antes da automação via Skill, foi realizada uma auditoria manual detalhada nos três projetos do repositório para catalogar falhas arquiteturais, brechas de segurança e code smells.

### 📦 Projeto 1: `code-smells-project` (Python / Flask 3.1.1 — E-commerce API)

| Severidade | Anti-pattern / Problema | Arquivo:Linhas | Justificativa de Relevância |
| :--- | :--- | :--- | :--- |
| 🔴 **CRITICAL** | **SQL Injection via Concatenação** | `models.py:28, 48, 58, 68, 92, 109, 140, 280, 291` | Parâmetros de entrada são interpolados diretamente em strings SQL sem prepared statements. Permite extração de dados sensíveis e destruição do banco. |
| 🔴 **CRITICAL** | **Hardcoded Secrets & Vazamento no `/health`** | `app.py:7`, `controllers.py:289` | `SECRET_KEY` fixada no código e exposta abertamente no JSON de `/health`, comprometendo sessões e tokens criptográficos. |
| 🔴 **CRITICAL** | **Endpoints Perigosos sem Autenticação** | `app.py:47-79` | Rotas `/admin/query` e `/admin/reset-db` permitem execução arbitrária de SQL e drop de dados sem qualquer autenticação. |
| 🔴 **CRITICAL** | **Senhas em Plaintext (Texto Puro)** | `models.py:83, 99, 110, 127` | Credenciais armazenadas e consultadas em texto puro no SQLite, violando conformidades básicas de segurança e privacidade. |
| 🟠 **HIGH** | **God File / Falta de Separação de Domínios** | `models.py:1-315` | Um único arquivo concentra queries, regras de negócio, persistência e cálculos de 4 domínios distintos (`produtos`, `usuarios`, `pedidos`, `relatorios`). |
| 🟡 **MEDIUM** | **Problema de Consultas N+1** | `models.py:187-199, 219-231` | Execução de queries em loop para buscar itens e nomes de produtos de cada pedido em vez de utilizar `JOIN`. |
| 🟢 **LOW** | **Magic Numbers & Logs com `print()`** | `models.py:257-263`, `controllers.py:8, 57, 106` | Valores mágicos soltos (`10000`, `0.1`, `5000`, `0.05`) e `print()` despadronizado em vez de logging configurável. |

---

### 📦 Projeto 2: `ecommerce-api-legacy` (Node.js / Express — LMS API com Checkout)

| Severidade | Anti-pattern / Problema | Arquivo:Linhas | Justificativa de Relevância |
| :--- | :--- | :--- | :--- |
| 🔴 **CRITICAL** | **Exposição de Chaves de Produção & Secrets** | `src/utils.js:1-7`, `src/AppManager.js:45` | Credenciais de banco, dados SMTP e chave privada do gateway (`pk_live_...`) hardcoded, com log de cartão de crédito no console. |
| 🔴 **CRITICAL** | **Criptografia Insegura (*Bad Crypto*)** | `src/utils.js:17-23` | Função `badCrypto` concatena pedaços repetidos de Base64 sem algoritmo criptográfico real, gerando hashes previsíveis e reversíveis. |
| 🟠 **HIGH** | **God Class (*AppManager*) & Pyramid of Doom** | `src/AppManager.js:4-139` | Classe única gerencia schema DDL, seeds, registro de rotas, pagamentos e relatórios com até 5 níveis de callbacks aninhados (*Callback Hell*). |
| 🟠 **HIGH** | **Estado Global Mutável em Memória** | `src/utils.js:9-10`, `src/AppManager.js:59` | `globalCache` e `totalRevenue` vivem no escopo do módulo Node.js, gerando condições de corrida (*race conditions*) e corrupção em concorrência. |
| 🟡 **MEDIUM** | **N+1 Query Pyramid no Relatório Financeiro** | `src/AppManager.js:83-128` | Consultas assíncronas aninhadas em 4 níveis (`courses -> enrollments -> users -> payments`) gerando dezenas de I/O desnecessários. |
| 🟢 **LOW** | **Nomenclatura Obscura / Variáveis Crípticas** | `src/AppManager.js:29-33` | Variáveis como `let u = req.body.usr`, `let e = req.body.eml`, `let cid = req.body.c_id` reduzem severamente a legibilidade. |

---

### 📦 Projeto 3: `task-manager-api` (Python / Flask — Task Manager API)

| Severidade | Anti-pattern / Problema | Arquivo:Linhas | Justificativa de Relevância |
| :--- | :--- | :--- | :--- |
| 🔴 **CRITICAL** | **Vazamento de Hashes de Senha na API** | `models/user.py:21`, `routes/user_routes.py:40, 85` | O método `to_dict()` da entidade `User` inclui `'password': self.password`, vazando hashes de senhas em retornos públicos de endpoints. |
| 🔴 **CRITICAL** | **Criptografia Fraca (MD5 sem Salt)** | `models/user.py:29, 32` | Uso de `hashlib.md5(pwd.encode()).hexdigest()` para senhas, vulnerável a ataques de tabela Rainbow e força bruta. |
| 🟠 **HIGH** | **Fat Routes & Lógica Presa no Controlador** | `routes/report_routes.py:13-100`, `routes/task_routes.py:12-63` | Rotas acumulam dezenas de linhas com cálculos estatísticos, contagens analíticas e formatações pesadas em vez de delegar a Services/Controllers. |
| 🟠 **HIGH** | **Credenciais SMTP Hardcoded** | `services/notification_service.py:9-10` | E-mail e senha de servidor de e-mail corporativo (`senha123`) expostas diretamente no código. |
| 🟡 **MEDIUM** | **Queries N+1 em Relatórios e Listagens** | `routes/report_routes.py:53-68`, `routes/task_routes.py:41-58` | Iteração sobre listas de tarefas executando `User.query.get()` e `Category.query.get()` individualmente a cada item. |
| 🟡 **MEDIUM** | **Tratamento de Exceções Vazio (*Bare Excepts*)** | `routes/task_routes.py:62, 236`, `routes/report_routes.py:186, 208` | Blocos `except:` sem tipo de exceção que engolem erros críticos e mascaram falhas com respostas genéricas. |
| 🟢 **LOW** | **Uso de APIs Obsoletas (*Deprecated API*)** | `models/task.py:15-16`, `routes/task_routes.py:31` | Uso de `datetime.utcnow()`, método depreciado a partir do Python 3.12 em favor de `datetime.now(timezone.utc)`. |

---

## 2. Construção da Skill

### 🧠 Decisões de Design da Skill

A skill `/refactor-arch` foi estruturada em `.claude/skills/refactor-arch/` com um arquivo orquestrador principal (`SKILL.md`) e 5 arquivos de referência em Markdown:

```
.claude/skills/refactor-arch/
├── SKILL.md                    # Orquestrador com o prompt operacional e ciclo de 3 fases
├── analysis-heuristics.md      # Heurísticas de detecção agnóstica de linguagem, framework e banco
├── anti-patterns-catalog.md    # Catálogo com 14 anti-patterns classificados por severidade
├── report-template.md          # Template oficial padronizado para os relatórios da Fase 2
├── mvc-guidelines.md           # Diretrizes da arquitetura alvo (Models, Views/Routes, Controllers, Config)
└── refactoring-playbook.md     # 8 padrões concretos de transformação Antes / Depois
```

### 🎯 Garantia de Agnosticismo de Tecnologia
A skill não assume uma linguagem específica:
- **Fase 1 (Análise)**: Analisa manifestos (`package.json`, `requirements.txt`, `go.mod`, etc.) e padrões de imports dinamicamente.
- **Fase 2 (Auditoria)**: Aplica conceitos fundamentais de engenharia de software (SOLID, OWASP Top 10, Coesão e Acoplamento, N+1 queries) válidos para qualquer linguagem orientada a objetos ou funcional.
- **Fase 3 (Refatoração)**: Utiliza a convenção universal de camadas MVC (`src/config/`, `src/models/`, `src/routes/` ou `src/views/`, `src/controllers/`, `src/services/`, `src/middlewares/` e `app.*` como *composition root*).

### 🛡️ Catálogo de Anti-Patterns Incluídos
O catálogo contém 14 anti-patterns distribuídos nas 4 faixas de severidade:
1. **CRITICAL**: SQL Injection, Hardcoded Secrets & Token Leaks, God Class / God File, Criptografia Quebrada / Plaintext, Endpoints Perigosos Não-Autenticados.
2. **HIGH**: Fat Routes / Negócio Preso no Controlador, Callback Hell / Pyramid of Doom, Estado Global Mutável em Memória.
3. **MEDIUM**: Consultas N+1, Tratamento de Exceções Inadequado (Bare Excepts), Ausência de Validação Estruturada.
4. **LOW**: Magic Numbers, Detecção de APIs Obsoletas (`datetime.utcnow()`), Logs Despadronizados com `print()` / `console.log()`.

### ⚠️ Desafios Encontrados e Soluções
* **Problema**: Manter contratos legados de API intactos durante a decomposição das God Classes.
  * **Solução**: Mapeamento rigoroso de rotas e campos nos controllers, mantendo retrocompatibilidade nos responses.
* **Problema**: Quebra de integridade referencial ao deletar usuários no projeto Node.js.
  * **Solução**: Configuração de `PRAGMA foreign_keys = ON` e exclusão transacional em cascata no `userModel.js`.
* **Problema**: Hashes de senhas vazando em endpoints públicos no projeto de Task Manager.
  * **Solução**: Omissão do campo `password` no método `to_dict()` e validação segura via PBKDF2/scrypt.

---

## 3. Resultados e Validação

### 📊 Resumo dos Relatórios de Auditoria

| Projeto | Stack | CRITICAL | HIGH | MEDIUM | LOW | Total Findings |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`code-smells-project`** | Python + Flask | 4 | 2 | 2 | 2 | **10** |
| **`ecommerce-api-legacy`** | Node.js + Express | 2 | 3 | 2 | 1 | **8** |
| **`task-manager-api`** | Python + Flask | 2 | 2 | 2 | 1 | **7** |

---

### 🔄 Comparativo Estrutural Antes / Depois

#### Projeto 1: `code-smells-project`
```diff
- code-smells-project/
- ├── app.py (God File com rotas, endpoints perigosos e secrets)
- ├── controllers.py (Controladores acoplados a prints e validações manuais)
- ├── models.py (315 linhas misturando 4 domínios com SQL Injection)
- └── database.py (Conexão global mutável sem pool)

+ code-smells-project/
+ ├── src/
+ │   ├── config/
+ │   │   ├── settings.py (Carregamento seguro de env e constantes)
+ │   │   └── database.py (Inicialização DDL e seeds com senhas em hash)
+ │   ├── models/
+ │   │   ├── produto_model.py (Queries parametrizadas e busca)
+ │   │   ├── usuario_model.py (Autenticação segura e hashing)
+ │   │   ├── pedido_model.py (Transações de pedidos e JOINs sem N+1)
+ │   │   └── relatorio_model.py (Cálculo de faturamento com constantes)
+ │   ├── controllers/
+ │   │   ├── produto_controller.py
+ │   │   ├── usuario_controller.py
+ │   │   ├── pedido_controller.py
+ │   │   ├── relatorio_controller.py
+ │   │   └── system_controller.py
+ │   ├── routes/
+ │   │   ├── produto_routes.py
+ │   │   ├── usuario_routes.py
+ │   │   ├── pedido_routes.py
+ │   │   ├── relatorio_routes.py
+ │   │   └── system_routes.py
+ │   ├── middlewares/
+ │   │   └── error_handler.py (Handler centralizado de erros JSON)
+ │   └── app.py (Fábrica de aplicação create_app)
+ └── app.py (Entrypoint raiz retrocompatível)
```

#### Projeto 2: `ecommerce-api-legacy`
```diff
- ecommerce-api-legacy/src/
- ├── AppManager.js (God Class com DDL, rotas, checkout e relatórios N+1)
- ├── app.js (Instanciação direta)
- └── utils.js (Secrets hardcoded, estado global mutável e badCrypto)

+ ecommerce-api-legacy/src/
+ ├── config/
+ │   ├── environment.js (Configurações via process.env)
+ │   └── database.js (Promisified SQLite com foreign keys)
+ ├── models/
+ │   ├── userModel.js (CRUD e deleção em cascata)
+ │   ├── courseModel.js (Consultas de cursos)
+ │   ├── enrollmentModel.js (Matrículas)
+ │   ├── paymentModel.js (Pagamentos e logs de auditoria)
+ │   └── reportModel.js (Relatório financeiro com JOINs otimizados)
+ ├── services/
+ │   ├── cryptoService.js (Hashing seguro com SHA-256/Salt)
+ │   ├── paymentService.js (Processamento de checkout com logs mascarados)
+ │   └── cacheService.js (Cache em memória encapsulado)
+ ├── controllers/
+ │   ├── checkoutController.js
+ │   ├── reportController.js
+ │   └── userController.js
+ ├── routes/
+ │   ├── checkoutRoutes.js
+ │   ├── reportRoutes.js
+ │   └── userRoutes.js
+ ├── middlewares/
+ │   └── errorHandler.js (Middleware Express centralizado de erros)
+ └── app.js (Composition Root assíncrono com bootstrap)
```

#### Projeto 3: `task-manager-api`
```diff
- task-manager-api/
- ├── models/ (User com MD5 e to_dict vazando senha; datetime.utcnow obsoleto)
- ├── routes/ (Fat routes com N+1 queries e bare excepts)
- ├── services/ (NotificationService com senha hardcoded)
- └── app.py (Configuração hardcoded)

+ task-manager-api/src/
+ ├── config/
+ │   ├── settings.py (Settings via os.getenv)
+ │   └── database.py (Instância desacoplada do SQLAlchemy)
+ ├── models/
+ │   ├── user_model.py (Hash com PBKDF2/scrypt, senha omitida do to_dict)
+ │   ├── category_model.py (Entidade Category)
+ │   └── task_model.py (Entidade Task com timezone aware)
+ ├── services/
+ │   ├── notification_service.py (Notificações seguras com fallback)
+ │   ├── task_service.py (Lógicas de negócio, busca e estatísticas)
+ │   └── report_service.py (Relatórios analíticos sem N+1 queries)
+ ├── controllers/
+ │   ├── user_controller.py
+ │   ├── task_controller.py
+ │   ├── category_controller.py
+ │   └── report_controller.py
+ ├── routes/
+ │   ├── user_routes.py
+ │   ├── task_routes.py
+ │   ├── category_routes.py
+ │   ├── report_routes.py
+ │   └── system_routes.py
+ ├── middlewares/
+ │   └── error_handler.py (Tratamento centralizado de erros)
+ └── app.py (Fábrica create_app)
+ └── app.py (Entrypoint raiz)
```

---

### ✅ Checklist de Validação (3/3 Projetos)

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python 3.14 e Node.js 24)
- [x] Framework detectado corretamente (Flask e Express)
- [x] Domínio da aplicação descrito corretamente (E-commerce, LMS, Task Manager)
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (10, 8 e 7 findings)
- [x] Detecção de APIs deprecated incluída (datetime.utcnow, MD5)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
```

---

### 📋 Logs de Validação das Aplicações

#### 🔹 Projeto 1 (`code-smells-project`):
```
--- TESTANDO ENDPOINTS DE CODE-SMELLS-PROJECT ---
[OK] [GET /health] OK - Sem vazamento de secret
[OK] [GET /] OK
[OK] [GET /produtos] OK - 10 produtos retornados
[OK] [GET /produtos/busca] OK - 3 itens encontrados
[OK] [POST /produtos] OK - Criado produto ID 11
[OK] [POST /login] OK - Autenticacao com senha hash validada com sucesso
[OK] [POST /pedidos] OK - Pedido criado com calculo correto
[OK] [GET /relatorios/vendas] OK - Relatorio gerado com sucesso

TODOS OS TESTES DO PROJETO 1 PASSARAM COM SUCESSO!
```

#### 🔹 Projeto 2 (`ecommerce-api-legacy`):
```
--- TESTANDO ENDPOINTS DE ECOMMERCE-API-LEGACY (NODE.JS) ---
LMS API refatorada rodando na porta 3000 (development)...
[PAYMENT] Processando transação de R$ 497 no cartão ****-****-****-4444
[CACHE] Salvando chave: last_checkout_2
[OK] [POST /api/checkout] Sucesso: enrollment_id=2
[PAYMENT] Processando transação de R$ 997 no cartão ****-****-****-4444
[OK] [POST /api/checkout] Recusado: status 400 correto
[OK] [GET /api/admin/financial-report] Sucesso: 2 cursos listados
[OK] [DELETE /api/users/1] Sucesso: Usuário e registros associados deletados com sucesso.

TODOS OS TESTES DO PROJETO 2 PASSARAM COM SUCESSO!
```

#### 🔹 Projeto 3 (`task-manager-api`):
```
--- TESTANDO ENDPOINTS DE TASK-MANAGER-API (PYTHON/FLASK) ---
[OK] [GET /health] OK
[OK] [POST /categories] Categoria criada ID 1
[OK] [POST /users] Usuario criado ID 1 - Hash omitido com seguranca
[OK] [POST /login] Autenticacao com senha PBKDF2/scrypt realizada com sucesso
[OK] [POST /tasks] Task criada ID 1
[OK] [GET /tasks] 1 tarefas listadas (sem queries N+1)
[OK] [GET /reports/summary] Relatorio gerado com sucesso
[OK] [GET /reports/user/1] Relatorio do usuario OK

TODOS OS TESTES DO PROJETO 3 PASSARAM COM SUCESSO!
```

---

## 4. Como Executar

### Pré-requisitos
- Python 3.10+ (instalado com pacotes `flask`, `flask-cors`, `flask-sqlalchemy`, `werkzeug`)
- Node.js 18+ e npm
- Claude Code (`claude`), Gemini CLI (`gemini`) ou Antigravity CLI (`agy`)

### Execução da Skill em Cada Projeto

```bash
# 1. Executar no Projeto 1 (Python / Flask)
cd code-smells-project
claude "/refactor-arch"
py verify_api.py

# 2. Executar no Projeto 2 (Node.js / Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"
node verify_api.js

# 3. Executar no Projeto 3 (Python / Flask)
cd ../task-manager-api
claude "/refactor-arch"
py verify_api.py
```

---

## 5. Estrutura do Repositório

```
mba-ia-refactor-projects-skill/
├── README.md                              # Documentação consolidada do desafio
│
├── reports/                               # Relatórios de auditoria gerados
│   ├── audit-project-1.md                 # Relatório da Fase 2 do Projeto 1
│   ├── audit-project-2.md                 # Relatório da Fase 2 do Projeto 2
│   └── audit-project-3.md                 # Relatório da Fase 2 do Projeto 3
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (E-commerce API)
│   ├── .claude/skills/refactor-arch/      # Skill e referências em Markdown
│   ├── src/                               # Código refatorado para MVC
│   ├── app.py                             # Entrypoint
│   └── verify_api.py                      # Script de validação
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API)
│   ├── .claude/skills/refactor-arch/      # Skill e referências em Markdown
│   ├── src/                               # Código refatorado para MVC
│   ├── api.http                           # Exemplos de chamadas HTTP
│   └── verify_api.js                      # Script de validação
│
└── task-manager-api/                      # Projeto 3 — Python/Flask (Task Manager API)
    ├── .claude/skills/refactor-arch/      # Skill e referências em Markdown
    ├── src/                               # Código refatorado para MVC
    ├── app.py                             # Entrypoint
    └── verify_api.py                      # Script de validação
```