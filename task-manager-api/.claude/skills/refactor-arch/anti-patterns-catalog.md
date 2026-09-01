# Catálogo de Anti-Patterns e Code Smells

Este catálogo contém a definição, sinais de detecção no código-fonte e severidade dos principais anti-patterns arquiteturais, de segurança e de qualidade de código.

---

## 🔴 Severidade CRITICAL

### 1. SQL Injection via Concatenação de Strings
* **Sinais de Detecção**:
  * Python: `cursor.execute("... " + var + " ...")`, `f"SELECT * FROM ... WHERE id = {var}"`, `"...".format(var)`.
  * Node.js: `db.run(`... ${var} ...`)`, `"SELECT * FROM ... WHERE id = " + id`.
* **Impacto**: Permite que atacantes executem comandos arbitrários no banco de dados, extraiam dados confidenciais ou destruam tabelas.
* **Recomendação**: Utilizar queries parametrizadas com placeholders (`?` ou `:param` no SQLite, `$1` no Postgres) ou ORM seguro.

### 2. Hardcoded Secrets & Credential Exposure
* **Sinais de Detecção**:
  * Variáveis com nomes `SECRET_KEY`, `PASSWORD`, `API_KEY`, `TOKEN`, `GATEWAY_KEY` contendo strings literais como `'minha-chave-123'`, `'senha_super_secreta'`, `'pk_live_...'`.
  * Exposição de chaves de configuração em endpoints de health check (ex: retornar `SECRET_KEY` no JSON de `/health`).
* **Impacto**: Comprometimento total da segurança do sistema, vazamento de chaves de produção em repositórios de código.
* **Recomendação**: Isolar em módulo `config` carregado estritamente via variáveis de ambiente (`os.getenv`, `process.env`) com `.env`.

### 3. God Class / God File
* **Sinais de Detecção**:
  * Arquivos ou classes com centenas de linhas contendo simultaneamente: inicialização de banco, DDL de tabelas, regras de negócio de múltiplos domínios, rotas HTTP e formatação de resposta.
  * Exemplos: `AppManager.js` com rotas, DB e checkout; `models.py` contendo queries de produtos, usuários, pedidos e relatórios juntos.
* **Impacto**: Impossibilidade de testar em isolamento, altíssimo acoplamento, qualquer alteração quebra múltiplos domínios.
* **Recomendação**: Decompor em classes/módulos dedicados seguindo o Princípio da Responsabilidade Única (SRP) em camadas MVC.

### 4. Criptografia Quebrada / Senhas em Plaintext / Vazamento de Hash
* **Sinais de Detecção**:
  * Senhas salvas em texto puro (`'admin123'`, `'123456'`) no banco.
  * Uso de funções fracas ou caseiras (`badCrypto`, `hashlib.md5(pwd.encode())` sem salt).
  * Serialização do campo `password` / hash de senha em métodos `to_dict()` expostos em retas de busca ou cadastro.
* **Impacto**: Roubo massivo de credenciais de usuários e quebra instantânea de privacidade.
* **Recomendação**: Utilizar algoritmos robustos com salt (Argon2, bcrypt, PBKDF2 ou `generate_password_hash`) e omitir senhas de qualquer saída de API.

### 5. Endpoints Perigosos e Não Autenticados
* **Sinais de Detecção**:
  * Rotas como `/admin/query` (executa SQL arbitrário recebido no body) ou `/admin/reset-db` (deleta todas as tabelas) expostas publicamente sem middleware de autenticação/autorização.
* **Impacto**: Destruição de dados por qualquer visitante da API.
* **Recomendação**: Remover endpoints de debug/backdoor ou proteger rigorosamente com autenticação de administrador e validação de permissão.

---

## 🟠 Severidade HIGH

### 6. Fat Routes / Negócio Preso no Controlador
* **Sinais de Detecção**:
  * Handlers de rota contendo loops de agregação de dados, cálculos financeiros, regras de negócio complexas, envio direto de emails e formatação complexa.
* **Impacto**: Dificuldade de reutilizar regras de negócio, impossibilidade de testes unitários sem levantar o servidor HTTP.
* **Recomendação**: Extrair a lógica de negócio para Services ou Models de domínio, mantendo Controllers focados apenas em receber req/res e coordenar.

### 7. Callback Hell & Pyramid of Doom
* **Sinais de Detecção**:
  * Em Node.js: aninhamento de 3 ou mais callbacks assíncronos (`db.get(..., () => { db.get(..., () => { db.run(..., () => { ... }) }) })`).
* **Impacto**: Fluxo de código ilegível, tratamento de erros inconsistente, vazamento de contexto.
* **Recomendação**: Promisify ou migrar para `async/await` com blocos `try/catch` limpos.

### 8. Estado Global Mutável em Memória
* **Sinais de Detecção**:
  * Variáveis globais mutáveis no escopo de módulo (ex: `globalCache = {}`, `totalRevenue = 0`, `db_connection = None` compartilhado globalmente sem thread-safety).
* **Impacto**: Race conditions em concorrência, corrupção de dados entre requisições de diferentes usuários.
* **Recomendação**: Encapsular estado em serviços injetáveis, bancos de dados ou stores apropriados (Redis, sessões gerenciadas).

---

## 🟡 Severidade MEDIUM

### 9. Problema de Consulta N+1 (N+1 Query Problem)
* **Sinais de Detecção**:
  * Execução de queries em loop (ex: iterar sobre pedidos e, para cada pedido, executar `SELECT * FROM itens_pedido` e `SELECT * FROM produtos`).
* **Impacto**: Degradação drástica de performance com aumento exponencial de roundtrips ao banco de dados.
* **Recomendação**: Utilizar `JOIN` SQL ou eager loading no ORM (`db.relationship`, `joinedload`).

### 10. Tratamento de Exceções Inadequado (Bare Excepts)
* **Sinais de Detecção**:
  * Blocos `except:` sem especificar a classe de exceção ou engolindo erros sem log adequado, retornando apenas status 500 genérico.
* **Impacto**: Dificuldade extrema de depuração e mascaramento de erros críticos de infraestrutura/sintaxe.
* **Recomendação**: Capturar exceções específicas, logar com contexto e delegar para um middleware centralizado de tratamento de erros.

### 11. Ausência de Validação Estruturada de Payload
* **Sinais de Detecção**:
  * Verificações manuais espalhadas e inconsistentes (`if not dados: return 400`, `if "nome" not in dados`) sem validação de tipos ou limites de tamanho.
* **Impacto**: Erros inesperados de runtime e respostas inconsistentes para o cliente.
* **Recomendação**: Centralizar validações em schemas de entrada ou middlewares dedicados.

---

## 🟢 Severidade LOW

### 12. Magic Numbers & Constantes Soltas
* **Sinais de Detecção**:
  * Números soltos em lógicas de negócio (ex: `10000`, `0.1`, `5000`, `0.05`, `4`, `200`, `'#000000'`) sem nome de constante explicativa.
* **Impacto**: Dificulta a leitura, compreensão da regra e manutenção futura.
* **Recomendação**: Declarar constantes com nomes semânticos (ex: `DISCOUNT_TIER_1_THRESHOLD`, `DISCOUNT_TIER_1_RATE`).

### 13. Uso de APIs Obsoletas / Deprecated APIs
* **Sinais de Detecção**:
  * Python: Uso de `datetime.utcnow()` (descontinuado a partir do Python 3.12 em favor de `datetime.now(timezone.utc)`).
  * Node.js: Uso de `new Buffer()` obsoleto ou métodos descontinuados de bibliotecas.
* **Impacto**: Avisos de depreciação (*DeprecationWarning*) e risco de quebra em versões futuras do runtime.
* **Recomendação**: Atualizar para as APIs modernas e recomendadas pelas documentações oficiais (`datetime.now(timezone.utc)`, `Buffer.from()`).

### 14. Logs Despadronizados com `print()` / `console.log()`
* **Sinais de Detecção**:
  * Chamadas a `print(...)` ou `console.log(...)` espalhadas no código em vez de bibliotecas estruturadas de logging.
* **Impacto**: Poluição do stdout, impossibilidade de filtrar por nível de log (DEBUG, INFO, WARN, ERROR).
* **Recomendação**: Configurar e utilizar um logger estruturado (módulo `logging` no Python ou `winston`/`pino` no Node.js).
