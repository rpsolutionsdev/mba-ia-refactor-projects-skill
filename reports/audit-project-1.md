================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] SQL Injection via Concatenação Direta
File: models.py:28, 48-50, 58-61, 68, 92, 109-111, 140, 149-150, 158-161, 164-165, 174, 280, 291-297
Description: Parâmetros recebidos de requisições HTTP (`id`, `nome`, `descricao`, `preco`, `estoque`, `categoria`, `email`, `senha`, `termo`, `novo_status`) são concatenados diretamente em strings SQL sem prepared statements ou sanitização.
Impact: Permite execução arbitrária de comandos SQL (exfiltração de dados, bypass de autenticação e destruição do banco).
Recommendation: Utilizar queries parametrizadas com placeholders `?` do sqlite3.

### [CRITICAL] Hardcoded Secrets e Vazamento de Credenciais na API
File: app.py:7-8, controllers.py:289
Description: A chave `SECRET_KEY` está hardcoded no arquivo `app.py` com o valor `'minha-chave-super-secreta-123'` e é exposta publicamente no payload de resposta do endpoint `/health`.
Impact: Quebra de integridade de sessões e tokens criptográficos da aplicação com exposição pública de segredos em produção.
Recommendation: Carregar segredos através de variáveis de ambiente (`os.getenv`) e remover credenciais da resposta de healthcheck.

### [CRITICAL] Endpoints Perigosos e Não Autenticados
File: app.py:47-79
Description: As rotas `/admin/reset-db` e `/admin/query` permitem deletar todas as tabelas do sistema e executar SQL arbitrário enviado via JSON sem qualquer camada de autenticação ou autorização.
Impact: Qualquer usuário não autenticado na rede pode apagar ou manipular o banco de dados livremente.
Recommendation: Remover ou proteger rigorosamente essas rotas de administração com middlewares de autenticação.

### [CRITICAL] Armazenamento de Senhas em Texto Puro (Plaintext Passwords)
File: models.py:83, 99, 110, 127-128
Description: As senhas dos usuários são salvas e validadas diretamente em texto puro no banco de dados SQLite sem qualquer função hash criptográfica.
Impact: Em caso de vazamento da base, todas as credenciais dos clientes e administradores ficam expostas imediatamente.
Recommendation: Utilizar `werkzeug.security.generate_password_hash` e `check_password_hash` para hashing seguro de senhas.

### [HIGH] God File / Falta de Separação de Domínios
File: models.py:1-315
Description: O arquivo `models.py` funciona como um *God File*, concentrando queries, regras de negócio, validações e relatórios de 4 domínios distintos (`produtos`, `usuarios`, `pedidos`, `relatorios`).
Impact: Impossibilidade de manutenção e testes isolados, alto acoplamento e violação do Princípio da Responsabilidade Única (SRP).
Recommendation: Decompor o arquivo em modelos e controladores segregados por domínio dentro de `src/models/` e `src/controllers/`.

### [HIGH] Regras de Negócio Presas em Controladores e Rotas
File: controllers.py:24-63, 188-221, models.py:133-170, 235-273
Description: Controladores e modelos acumulam regras de validação complexas, envio de notificações fictícias (`print`) e cálculos de regras de negócio de checkout e relatórios.
Impact: Dificulta a reutilização de regras de negócio e testes automatizados de fluxo.
Recommendation: Extrair regras de negócio para serviços e modelos de domínio especializados.

### [MEDIUM] Problema de Consulta N+1 (N+1 Queries)
File: models.py:187-200, 219-232
Description: As funções `get_pedidos_usuario` e `get_todos_pedidos` realizam queries em loop para buscar os itens de cada pedido e o nome de cada produto individualmente.
Impact: Degradação severa de desempenho conforme o volume de pedidos e itens cresce.
Recommendation: Utilizar `JOIN` SQL para trazer pedidos, itens e produtos em uma única consulta estruturada.

### [MEDIUM] Falta de Tratamento Centralizado de Erros
File: controllers.py:10-12, 60-62, 95-96, 108-109, 125-126, 143-144, 164-165, 185-186, 218-220, 234-235, 254-255, 261-262, 291-292
Description: Blocos `try/except Exception as e` repetidos em todos os métodos dos controladores com retorno manual de status 500 e prints sem padrão.
Impact: Código redundante e inconsistência de formato em mensagens de erro para o cliente.
Recommendation: Criar middleware/error handler global para capturar exceções não tratadas e padronizar as respostas.

### [LOW] Magic Numbers em Regras de Desconto e Paginação
File: models.py:257-263
Description: Valores mágicos soltos (`10000`, `0.1`, `5000`, `0.05`, `1000`, `0.02`) sem constantes semânticas.
Impact: Reduz a legibilidade do código e dificulta a manutenção de regras comerciais.
Recommendation: Declarar constantes descritivas no módulo de configuração ou constantes de negócio.

### [LOW] Uso de `print()` em vez de Logging Estruturado
File: app.py:56, 83-86, controllers.py:8, 57, 106, 161, 179, 182, 208-210, 248, 250
Description: Uso de `print()` para logs de operação, auditoria e erros em toda a aplicação.
Impact: Impossibilidade de controlar níveis de severidade (DEBUG, INFO, ERROR) e exportar logs em formato estruturado.
Recommendation: Configurar o módulo padrão `logging` do Python.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
