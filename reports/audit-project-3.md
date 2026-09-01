================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.1.1 (Flask-SQLAlchemy)
Files:   9 analyzed | ~1100 lines of code

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] Vazamento de Hashes de Senha no Payload JSON da API
File: models/user.py:21, routes/user_routes.py:40, 85, 129
Description: O método `to_dict()` da entidade `User` inclui explicitamente o atributo `'password': self.password`, expondo o hash das senhas dos usuários nos endpoints públicos de consulta (`GET /users`, `GET /users/:id`) e cadastro (`POST /users`).
Impact: Exposição massiva de hashes de senhas que permite a invasores aplicar dicionários e ataques de força bruta offline.
Recommendation: Remover o campo `password` de todas as saídas de serialização pública do usuário.

### [CRITICAL] Criptografia Fraca e Insegura (MD5 sem Salt)
File: models/user.py:29, 32
Description: As senhas são processadas via `hashlib.md5(pwd.encode()).hexdigest()`. O algoritmo MD5 é criptograficamente vulnerável a colisões e ataques de tabela Rainbow por não utilizar salt ou funções de derivação de chave lentas.
Impact: Quebra quase instantânea de senhas curtas ou comuns de usuários.
Recommendation: Migrar para `werkzeug.security.generate_password_hash` (PBKDF2/scrypt com salt) e `check_password_hash`.

### [HIGH] Credenciais Hardcoded e Falta de Configuração Segura
File: app.py:13, services/notification_service.py:9-10
Description: A chave `SECRET_KEY = 'super-secret-key-123'` e credenciais de servidor de email (`email_user = 'taskmanager@gmail.com'`, `email_password = 'senha123'`) estão fixadas no código-fonte.
Impact: Risco de invasão e comprometimento de contas corporativas de email em caso de compartilhamento do código.
Recommendation: Isolar todas as configurações e credenciais em `src/config/settings.py` carregadas via variáveis de ambiente.

### [HIGH] Fat Routes / Violação do Padrão MVC e Princípios SOLID
File: routes/report_routes.py:13-100, routes/task_routes.py:12-63
Description: Handlers de rotas acumulam lógicas de negócio pesadas, cálculos analíticos de produtividade, regras de atraso de tarefas e formatações complexas diretamente dentro dos arquivos de rota em vez de delegar para Controllers e Services.
Impact: Alto acoplamento, duplicação de regras de negócio e impossibilidade de testes unitários isolados.
Recommendation: Reestruturar o projeto no padrão MVC com Controllers orquestradores e Services de domínio dedicados.

### [MEDIUM] Problema de Consultas N+1 (N+1 Queries)
File: routes/report_routes.py:53-68, routes/task_routes.py:41-58
Description: No relatório de resumo, a aplicação itera sobre todos os usuários executando `Task.query.filter_by(user_id=u.id).all()` para cada usuário. Na listagem de tarefas, executa `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` em loop para cada tarefa.
Impact: Explosão de queries ao banco de dados e lentidão exponencial na API.
Recommendation: Utilizar `db.joinedload` ou queries de agregação SQL agrupadas com `JOIN` e `COUNT`.

### [MEDIUM] Tratamento de Exceções Inadequado (Bare Excepts)
File: routes/task_routes.py:62, 137, 236, routes/report_routes.py:186, 208, 221, routes/user_routes.py:130, 150
Description: Vários endpoints usam blocos `except:` vazios sem capturar tipos específicos de erro, retornando respostas 500 sem log estruturado da causa raiz.
Impact: Mascara bugs de sintaxe e erros de banco de dados, tornando a depuração extremamente difícil.
Recommendation: Capturar exceções específicas com logs apropriados e utilizar handlers centralizados de erro.

### [LOW] Uso de APIs Obsoletas (Deprecated APIs)
File: models/task.py:15-16, routes/task_routes.py:31, routes/report_routes.py:45, services/notification_service.py:35, utils/helpers.py:38
Description: Uso extensivo de `datetime.utcnow()`, método marcado como descontinuado/deprecated a partir do Python 3.12 em favor de timestamps conscientes de timezone (`datetime.now(timezone.utc)`).
Impact: Alertas de depreciação e possíveis falhas de compatibilidade futura em runtimes modernos.
Recommendation: Substituir todas as ocorrências por `datetime.now(timezone.utc)`.

================================
Total: 7 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
